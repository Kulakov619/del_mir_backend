from django.contrib import admin
from django.contrib.auth.admin import Group
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.admin import UserAdmin
from django.utils.text import gettext_lazy as _

from .models import AuthTransaction
from .models import OTPValidation
from .models import Role
from .models import User
from .models import Address
from .models import DopMobile


class UsrAdrInline(admin.TabularInline):
    model = Address
    extra = 0


class UsrDmInline(admin.TabularInline):
    model = DopMobile
    extra = 0


class DRFUserAdmin(admin.ModelAdmin):
    inlines = (UsrAdrInline, UsrDmInline, )
    list_display = ("username", "email", "name", "mobile", "is_staff")
    search_fields = ("username", "name", "email", "mobile")


class OTPValidationAdmin(admin.ModelAdmin):
    list_display = ("destination", "otp", "prop")


class AuthTransactionAdmin(admin.ModelAdmin):
    list_display = ("created_by", "ip_address", "create_date")

    def has_add_permission(self, request):
        """Limits admin to add an object."""
        return False

    def has_change_permission(self, request, obj=None):
        """Limits admin to change an object."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Limits admin to delete an object."""
        return False


admin.site.unregister(Group)
admin.site.register(Role, GroupAdmin)
admin.site.register(User, DRFUserAdmin)
admin.site.register(OTPValidation, OTPValidationAdmin)
admin.site.register(AuthTransaction, AuthTransactionAdmin)

