from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
<<<<<<< HEAD
    name = "users"

    def ready(self):
        import users.signals
=======
    name = "users"
>>>>>>> Goncalo
