from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

   # Auto‑create a Profile when a User is created:
    def ready(self):
        from . import signals #noqa
