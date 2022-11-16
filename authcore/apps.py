from django.apps import AppConfig


class AuthCoreAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authcore'
    verbose_name = 'Авторизация и личный кабинет'

    def ready(self):
        from . import update_user_settings
        from .signals.handlers import post_register  # noqa
        update_user_settings()
