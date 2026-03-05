from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core" #Used by django to locate the app's models, migrations, templates etc.
    
    def ready(self):
        import core.signals #Without this, signal handlers defined 
        #in signals.py might never be connecetd
        
#ready() method called by django once when the app starts
#Performs initialization tasks that need to happen when the app starts up
# Common uses:
# Registering signal handlers
# Setting up background tasks
# Performing startup checks