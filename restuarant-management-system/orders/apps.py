from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"

    def ready(self):
        """Import order signals when Django starts the orders app."""
        import orders.signals  # noqa: F401


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# OrdersConfig configures the orders app for Django.
#
# default_auto_field tells Django to use BigAutoField for automatic primary
# keys. This matches the project setting and keeps model IDs consistent.
#
# name tells Django the Python path of this app.
#
# ready runs when Django finishes loading the app registry. It imports
# orders.signals so the signal handlers are connected before orders are saved.
#
# Important decisions that were made and why
#
# The signals are imported inside ready instead of at the top of the file.
# This is Django's recommended pattern because it avoids loading models before
# the app registry is ready.
#
# The import has noqa: F401 because the import is needed for its side effect:
# connecting signal receivers. The imported module name is not used directly.
#
# What you should read and understand before you review the code
#
# Read Django AppConfig and the ready method.
#
# Read why signal modules are usually imported in ready.
#
# ============================================================
# END OF REVIEW
# ============================================================
