import datetime
from typing import Dict
from typing import Optional
from typing import Union
import smtplib
from django.conf import settings
from django.core.mail import send_mail
from django.core.exceptions import ValidationError

import pytz
from django.http import HttpRequest
from django.utils import timezone
from django.utils.text import gettext_lazy as _
from rest_framework.exceptions import APIException
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.utils import datetime_from_epoch
from smsaero import SmsAero

from authcore import update_user_settings
from .models import AuthTransaction
from .models import OTPValidation
from .models import User

user_settings: Dict[
    str, Union[bool, Dict[str, Union[int, str, bool]]]
] = update_user_settings()
otp_settings: Dict[str, Union[str, int]] = user_settings["OTP"]


def get_client_ip(request: HttpRequest) -> Optional[str]:
    """
    Fetches the IP address of a client from Request and
    return in proper format.
    Source: https://stackoverflow.com/a/4581997

    Parameters
    ----------
    request: django.http.HttpRequest

    Returns
    -------
    ip: str or None
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    else:
        return request.META.get("REMOTE_ADDR")


def datetime_passed_now(source: datetime.datetime) -> bool:
    """
    Compares provided datetime with current time on the basis of Django
    settings. Checks source is in future or in past. False if it's in future.
    Parameters
    ----------
    source: datetime object than may or may not be naive

    Returns
    -------
    bool

    Author: Himanshu Shankar (https://himanshus.com)
    """
    if source.tzinfo is not None and source.tzinfo.utcoffset(source) is not None:
        return source <= datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    else:
        return source <= datetime.datetime.now()


def check_unique(prop: str, value: str) -> bool:
    """
    This function checks if the value provided is present in Database
    or can be created in DBMS as unique data.
    Parameters
    ----------
    prop: str
        The model property to check for. Can be::
            email
            mobile
            username
    value: str
        The value of the property specified

    Returns
    -------
    bool
        True if the data sent is doesn't exist, False otherwise.
    Examples
    --------
    To check if test@testing.com email address is already present in
    Database
    >>> print(check_unique('email', 'test@testing.com'))
    True
    """
    user = User.objects.extra(where=[prop + " = '" + value + "'"])
    return user.count() == 0


def generate_otp(prop: str, value: str) -> OTPValidation:
    """
    This function generates an OTP and saves it into Model. It also
    sets various counters, such as send_counter,
    is_validated, validate_attempt.
    Parameters
    ----------
    prop: str
        This specifies the type for which OTP is being created. Can be::
            email
            mobile
    value: str
        This specifies the value for which OTP is being created.

    Returns
    -------
    otp_object: OTPValidation
        This is the instance of OTP that is created.
    Examples
    --------
    To create an OTP for an Email test@testing.com
    >>> print(generate_otp('email', 'test@testing.com'))
    OTPValidation object

    >>> print(generate_otp('email', 'test@testing.com').otp)
    5039164
    """
    # Create a random number
    random_number: str = User.objects.make_random_password(
        length=otp_settings["LENGTH"], allowed_chars=otp_settings["ALLOWED_CHARS"]
    )

    # Checks if random number is unique among non-validated OTPs and
    # creates new until it is unique.
    while OTPValidation.objects.filter(otp__exact=random_number).filter(
        is_validated=False
    ):
        random_number: str = User.objects.make_random_password(
            length=otp_settings["LENGTH"], allowed_chars=otp_settings["ALLOWED_CHARS"]
        )

    # Get or Create new instance of Model with value of provided value
    # and set proper counter.
    try:
        otp_object: OTPValidation = OTPValidation.objects.get(destination=value)
    except OTPValidation.DoesNotExist:
        otp_object: OTPValidation = OTPValidation()
        otp_object.destination = value
    else:
        if not datetime_passed_now(otp_object.reactive_at):
            return otp_object

    otp_object.otp = random_number
    otp_object.prop = prop

    # Set is_validated to False
    otp_object.is_validated = False

    # Set attempt counter to OTP_VALIDATION_ATTEMPTS, user has to enter
    # correct OTP in 3 chances.
    otp_object.validate_attempt = otp_settings["VALIDATION_ATTEMPTS"]

    otp_object.reactive_at = timezone.now() - datetime.timedelta(minutes=1)
    otp_object.save()
    return otp_object


def send_otp(value: str, otpobj: OTPValidation, recip: str) -> Dict:

    otp: str = otpobj.otp

    if not datetime_passed_now(otpobj.reactive_at):
        raise PermissionDenied(
            detail=_(f"Отправка OTP не разрешена, пока: {otpobj.reactive_at}")
        )

    message = (
        f"Ваш одноразовый пароль {otp}. "
        f"Не пересылайте его никому!"
    )

    try:
        rdata: dict = send_message(message, otp_settings["SUBJECT"], [value], [recip])
    except ValueError as err:
        raise APIException(_(f"Сервер не отвечает: {err}"))

    otpobj.reactive_at = timezone.now() + datetime.timedelta(
        minutes=otp_settings["COOLING_PERIOD"]
    )
    otpobj.save()

    return rdata


def login_user(user: User, request: HttpRequest) -> Dict[str, str]:
    """
    This function is used to login a user. It saves the authentication in
    AuthTransaction model.

    Parameters
    ----------
    user: django.contrib.auth.get_user_model
    request: HttpRequest

    Returns
    -------
    dict:
        Generated JWT tokens for user.
    """
    token: RefreshToken = RefreshToken.for_user(user)

    # Add custom claims
    if hasattr(user, "email"):
        token["email"] = user.email

    if hasattr(user, "mobile"):
        token["mobile"] = user.mobile

    if hasattr(user, "name"):
        token["name"] = user.name

    user.last_login = timezone.now()
    user.save()

    AuthTransaction(
        created_by=user,
        ip_address=get_client_ip(request),
        token=str(token.access_token),
        refresh_token=str(token),
        session=user.get_session_auth_hash(),
        expires_at=datetime_from_epoch(token["exp"]),
    ).save()

    return {
        "refresh_token": str(token),
        "token": str(token.access_token),
        "session": user.get_session_auth_hash(),
    }


def check_validation(value: str) -> bool:
    """
    This functions check if given value is already validated via OTP or not.
    Parameters
    ----------
    value: str
        This is the value for which OTP validation is to be checked.

    Returns
    -------
    bool
        True if value is validated, False otherwise.
    Examples
    --------
    To check if 'test@testing.com' has been validated!
    >>> print(check_validation('test@testing.com'))
    True

    """
    try:
        otp_object: OTPValidation = OTPValidation.objects.get(destination=value)
        return otp_object.is_validated
    except OTPValidation.DoesNotExist:
        return False


def validate_otp(value: str, otp: int) -> bool:
    try:
        otp_object: OTPValidation = OTPValidation.objects.get(
            destination=value, is_validated=False
        )
    except OTPValidation.DoesNotExist:
        raise NotFound(
            detail=_(
                "Код уже не активен или деактивирован."
                "Пожалуйста, отправьте код снова."
            )
        )
    # Decrement validate_attempt
    otp_object.validate_attempt -= 1

    if str(otp_object.otp) == str(otp):
        # match otp
        otp_object.is_validated = True
        otp_object.save()
        return True

    elif otp_object.validate_attempt <= 0:
        # check if attempts exceeded and regenerate otp and raise error
        generate_otp(otp_object.prop, value)
        raise AuthenticationFailed(
            detail=_("Неверный одноразовый пароль! Отправьте еще раз.")
        )

    else:
        # update attempts and raise error
        otp_object.save()
        raise AuthenticationFailed(
            detail=_(
                f"Проверка пароля неудачная! Осталось {otp_object.validate_attempt} попытки(а)!"
            )
        )


def get_mobile_number(mobile):
    """
    Returns a mobile number after removing blanks
    Parameters
    ----------
    mobile: str

    Returns
    -------
    str
    """
    blanks = [' ', '.', ',', '(', ')', '-']

    for b in blanks:
        mobile = mobile.replace(b, '')

    return mobile


def validate_email(email):
    """
    Validates an email address
    Parameters
    ----------
    email: str

    Returns
    -------
    bool
    """
    from django.core.validators import validate_email

    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def send_message(message: str, subject: str, recip: list, recip_email: list,
                 html_message: str = None):

    sent = {'success': False, 'message': None}

    if not getattr(settings, 'EMAIL_HOST', None):
        raise ValueError('EMAIL_HOST must be defined in django '
                         'setting for sending mail.')
    if not getattr(settings, 'EMAIL_FROM', None):
        raise ValueError('EMAIL_FROM must be defined in django setting '
                         'for sending mail. Who is sending email?')
    if not getattr(settings, 'EMAIL_FROM', None):
        raise ValueError('EMAIL_FROM must be defined in django setting '
                         'for sending mail. Who is sending email?')

    # Check if there is any recipient
    if not len(recip) > 0:
        raise ValueError('Нет адресата.')
    # Check if the value of recipient is valid (min length: a@b.c)
    elif len(recip[0]) < 5:
        raise ValueError('Неверный адресат.')

    # Check if all recipient in list are of same type
    is_email = validate_email(recip[0])
    for ind in range(len(recip)):
        if validate_email(recip[ind]) is not is_email:
            raise ValueError('Неверный тип почты.')
        elif not is_email:
            recip[ind] = get_mobile_number(recip[ind])

    if isinstance(recip, str):
        # For backsupport
        recip = [recip]

    if is_email:
        try:
            send_mail(subject=subject, message=message,
                      html_message=html_message,
                      from_email=settings.EMAIL_FROM, recipient_list=recip)
        except smtplib.SMTPException as ex:
            sent['message'] = 'письмо не отправлено!' + str(ex.args)
            sent['success'] = False
        else:
            sent['message'] = 'письмо успешно отправлено!'
            sent['success'] = True

    else:
        try:
            api = SmsAero(settings.SMS_EMAIL, settings.SMS_API)
            api.sign_add("sc619.ru")
            send = api.send(recip, message)

        except Exception as ex:
            sent['message'] = 'cообщение не отправлено!' + str(ex.args)
            sent['success'] = False
            send_message(message=message, subject=subject,
                         recip=recip_email,
                         recip_email=recip_email,
                         html_message=html_message)
        else:
            if send['success']:
                sent['message'] = 'cообщение успешно отправлено!'
                sent['success'] = True
            else:
                sent['message'] = 'cообщение не отправлено!' + send['message']
                sent['success'] = False
    return sent


def json_serial(obj):
    """
    JSON serializer for objects not serializable by default json code
    Sources: [https://stackoverflow.com/a/22238613,
    https://stackoverflow.com/a/41200652,
    https://github.com/chartmogul/chartmogul-python/blob/master/chartmogul/resource.py]
    """
    from datetime import datetime, time

    if isinstance(obj, (datetime, time)):
        serial = obj.isoformat()
        return serial
    else:
        return "Non-Serializable Data"