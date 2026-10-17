from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core" #Used by django to locate the app's models, migrations, templates etc.
    def ready(self):
        import os
        import sys
        import threading
        import core.signals

        skip_commands = {"migrate", "makemigrations", "collectstatic", "test", "check"}
        if any(cmd in sys.argv for cmd in skip_commands):
            return

        # In runserver, only load in the worker process (RUN_MAIN == 'true'), not the monitor process
        if "runserver" in sys.argv and os.environ.get("RUN_MAIN") != "true":
            return

        def _warmup_models():
            try:
                from core.utils.embeddings import get_image_model, get_text_model
                get_image_model()
                get_text_model()
            except Exception:
                pass

        threading.Thread(target=_warmup_models, daemon=True).start()