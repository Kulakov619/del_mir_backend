from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import Group
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.text import gettext_lazy as _

from .managers import UserManager
from .variables import DESTINATION_CHOICES
from .variables import EMAIL


class Role(Group):

    class Meta:
        proxy = True
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True, db_column='created')
    updated = models.DateTimeField(auto_now=True, db_column='updated')

    class Meta:
        abstract = True


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        verbose_name=_("User name"), max_length=254, unique=True
    )
    email = models.EmailField(verbose_name=_("email address"), unique=True)
    mobile = models.CharField(
        verbose_name=_("mobile number"),
        max_length=12,
        unique=True,
        null=True,
        blank=True,
    )
    last_name = models.CharField(verbose_name=_("lastname"), max_length=500, blank=True)
    name = models.CharField(verbose_name=_("name"), max_length=500, blank=False)
    o_name = models.CharField(verbose_name=_("o_name"), max_length=500, blank=True)
    profile_image = models.ImageField(
        verbose_name=_("Profile Photo"), upload_to="user_images", null=True, blank=True
    )
    birthday = models.DateField(_('дата рождения'), blank=True, null=True)
    is_man = models.BooleanField(verbose_name=_("male"), blank=True, null=True)
    date_joined = models.DateTimeField(verbose_name=_("Date Joined"), auto_now_add=True)
    update_date = models.DateTimeField(verbose_name=_("Date Modified"), auto_now=True)
    is_active = models.BooleanField(verbose_name=_("Activated"), default=False)
    is_staff = models.BooleanField(verbose_name=_("Staff Status"), default=False)

    groups = models.ManyToManyField(
        Role,
        verbose_name=_("Roles"),
        blank=True,
        help_text=_(
            "The roles this user belongs to. A user will get all permissions "
            "granted to each of their roles."
        ),
        related_name="user_set",
        related_query_name="user",
    )

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["name", "email"]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def get_full_name(self) -> str:
        return f"{self.last_name} {self.name} {self.o_name}"

    def __str__(self):
        return f"{self.name} {self.mobile}"


class AuthTransaction(models.Model):
    """
    Represents all authentication in the system that took place via
    REST API.
    """
    ip_address = models.GenericIPAddressField(blank=False, null=False)
    token = models.TextField(verbose_name=_("JWT Access Token"))
    session = models.TextField(verbose_name=_("Session Passed"))
    refresh_token = models.TextField(
        blank=True,
        verbose_name=_("JWT Refresh Token"),
    )
    expires_at = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Expires At")
    )
    create_date = models.DateTimeField(
        verbose_name=_("Create Date/Time"), auto_now_add=True
    )
    update_date = models.DateTimeField(
        verbose_name=_("Date/Time Modified"), auto_now=True
    )
    created_by = models.ForeignKey(to=User, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.created_by.name) + " | " + str(self.created_by.username)

    class Meta:
        verbose_name = _("Authentication Transaction")
        verbose_name_plural = _("Authentication Transactions")


class OTPValidation(models.Model):
    """
    Represents all OTP Validation in the System.
    """
    otp = models.CharField(verbose_name=_("OTP code"), max_length=10)
    destination = models.CharField(
        verbose_name=_("destination Address (mobile/email)"),
        max_length=254,
        unique=True,
    )
    create_date = models.DateTimeField(verbose_name=_("create Date"), auto_now_add=True)
    update_date = models.DateTimeField(verbose_name=_("date modified"), auto_now=True)
    is_validated = models.BooleanField(verbose_name=_("is validated"), default=False)
    validate_attempt = models.IntegerField(
        verbose_name=_("attempted validation"), default=3
    )
    prop = models.CharField(
        verbose_name=_("destination property"),
        default=EMAIL,
        max_length=3,
        choices=DESTINATION_CHOICES,
    )
    send_counter = models.IntegerField(verbose_name=_("OTP sent counter"), default=0)
    sms_id = models.CharField(
        verbose_name=_("SMS ID"), max_length=254, null=True, blank=True
    )
    reactive_at = models.DateTimeField(verbose_name=_("ReActivate sending OTP"))

    def __str__(self):
        return self.destination

    class Meta:
        verbose_name = _("OTP Validation")
        verbose_name_plural = _("OTP Validations")


class Address(TimeStampedMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sity = models.CharField(_('город'), max_length=255)
    avenue = models.CharField(_('улица'), max_length=255)
    d = models.CharField(_('дом'), max_length=10)
    kv = models.CharField(_('квартира'), max_length=10, blank=True, null=True)
    is_default = models.BooleanField(verbose_name=_("адрес по умолчанию"), default=False)

    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')
        ordering = ['is_default', ]

    def __str__(self):
        if self.kv or self.kv != '':
            return f"{self.sity}, {self.avenue} {self.d}, кв. {self.kv}"
        else:
            return f"{self.sity}, {self.avenue} {self.d}"


class DopMobile(TimeStampedMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mobile = models.CharField(
        verbose_name=_("mobile number"),
        max_length=150,
        unique=True,
        null=True,
        blank=True,
    )
    confirmed = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('user phone')
        verbose_name_plural = _('user phones')
        ordering = ['id', ]

    def __str__(self):
        return self.mobile