from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator
from django.core.validators import ValidationError
from django.utils.text import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.serializers import SerializerMethodField

from authcore import user_settings
from .models import User, DopMobile, Address
from .utils import check_validation
from .variables import EMAIL
from .variables import MOBILE


class DopMobileSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = DopMobile
        fields = (
            'id',
            'mobile',
            'confirmed',
            'user',
        )


class AddressSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Address
        fields = (
            'id',
            'sity',
            'avenue',
            'd',
            'kv',
            'user'
        )
        read_only_fields = ('id', )


class UserSerializer(serializers.ModelSerializer):
    address = SerializerMethodField()
    dop_mobile = serializers.SerializerMethodField()

    def validate_email(self, value: str) -> str:
        if not user_settings["EMAIL_VALIDATION"]:
            return value

        if check_validation(value=value):
            return value
        else:
            raise serializers.ValidationError(
                "При смене почты необходимо верифицировать новый адрес."
            )

    def validate_mobile(self, value: str) -> str:
        if not user_settings["MOBILE_VALIDATION"]:
            return value

        if check_validation(value=value):
            return value
        else:
            raise serializers.ValidationError(
                "При смене номера телефона необходимо верифицировать новый номер."
            )

    def get_address(self, obj):
        customer_account_query = Address.objects.filter(
            user=obj.id)
        serializer = AddressSerializer(customer_account_query, many=True)

        return serializer.data


    def get_dop_mobile(self, obj):
        customer_account_query = DopMobile.objects.filter(
            user=obj.id)
        serializer = DopMobileSerializer(customer_account_query, many=True)

        return serializer.data

    class Meta:
        model = User
        fields = (
            "id",
            "last_name",
            "name",
            "o_name",
            "birthday",
            "is_man",
            "email",
            "mobile",
            "address",
            "dop_mobile",
        )


class UserShowSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("id", "username", "name")
        read_only_fields = ("username", "name")


class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    is_login = serializers.BooleanField(default=False)
    verify_otp = serializers.CharField(required=False)
    destination = serializers.CharField(required=True)
    id_mob = serializers.IntegerField(required=False)

    def get_user(self, prop: str, destination: str) -> User:
        if prop == MOBILE:
            try:
                user = User.objects.get(mobile=destination)
            except User.DoesNotExist:
                user = None
        else:
            try:
                user = User.objects.get(email=destination)
            except User.DoesNotExist:
                user = None
        return user

    def get_mobile(self, id_mob) -> DopMobile:
        try:
            dm = DopMobile.objects.get(pk=id_mob)
        except DopMobile.DoesNotExist:
            dm = None
        return dm

    def validate(self, attrs: dict) -> dict:
        validator = EmailValidator()
        try:
            validator(attrs["destination"])
        except ValidationError:
            attrs["prop"] = MOBILE
        else:
            attrs["prop"] = EMAIL

        user = self.get_user(attrs.get("prop"), attrs.get("destination"))

        if not user:
            if attrs["is_login"]:
                raise NotFound(_("Пользователь не найден"))
            elif "id_mob" in attrs.keys():
                dm = self.get_mobile(attrs.get("id_mob"))
                if not dm:
                    raise serializers.ValidationError(
                        _(
                            "Номер не найден!"
                        )
                    )
                elif dm.mobile != attrs["destination"]:
                    raise serializers.ValidationError(
                        _(
                            "Номер не соотвествует id записи!"
                        )
                    )
                else:
                    return attrs
            elif "email" not in attrs.keys() and "verify_otp" not in attrs.keys():
                raise serializers.ValidationError(
                    _(
                        "Пользователь не найден!"
                    )
                )
        else:
            attrs["email"] = user.email
            attrs["user"] = user
        return attrs


class CheckUniqueSerializer(serializers.Serializer):
    prop = serializers.ChoiceField(choices=("email", "mobile", "username"))
    value = serializers.CharField()


class OTPLoginRegisterSerializer(serializers.Serializer):
    lastname = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    mobile = serializers.CharField(required=True)
    verify_otp = serializers.CharField(default=None, required=False)

    @staticmethod
    def get_user(email: str, mobile: str):
        try:
            user = User.objects.get(email=email, mobile=mobile)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(mobile=mobile)
                except User.DoesNotExist:
                    user = None

        if user:
            if user.email == email and user.mobile == mobile:
                raise serializers.ValidationError(
                    _(
                        "Такой аккаунт уже зарегистрирован! "
                    )
                )
            if user.email != email:
                raise serializers.ValidationError(
                    _(
                        "Ваш аккаунт уже зарегистрирован на номер {mobile}! "
                        "Пожалуйста войдите с помощью одноразового пароля по номеру "
                        "телефона.".format(mobile=mobile, email=email)
                    )
                )
            if user.mobile != mobile:
                raise serializers.ValidationError(
                    _(
                        "Ваш аккаунт уже зарегистрирован на почту {email}! "
                        "Пожалуйста войдите с помощью одноразового пароля через "
                        "почту".format(mobile=mobile, email=email)
                    )
                )
        return user

    def validate(self, attrs: dict) -> dict:
        attrs["user"] = self.get_user(
            email=attrs.get("email"), mobile=attrs.get("mobile")
        )
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def get_user(self, destination: str) -> User:
        try:
            user = User.objects.get(email=destination)
        except User.DoesNotExist:
            user = None

        return user

    def validate(self, attrs: dict) -> dict:
        validator = EmailValidator()
        validator(attrs.get("email"))
        user = self.get_user(attrs.get("email"))

        if not user:
            raise NotFound(_("User with the provided email does not exist."))

        return attrs


class ImageSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=True)

    class Meta:
        model = User
        fields = ("profile_image",)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "no_active_account": _("username or password is invalid.")
    }

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        if hasattr(user, "email"):
            token["email"] = user.email

        if hasattr(user, "mobile"):
            token["mobile"] = user.mobile

        if hasattr(user, "name"):
            token["name"] = user.name
        return token
