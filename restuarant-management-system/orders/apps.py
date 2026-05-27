from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"

    def ready(self):
        """Import order signals when Django starts the orders app."""
        import orders.signals  # noqa: F401


