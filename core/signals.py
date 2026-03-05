from django.db.models.signals import post_save #signal sent after save() is called
from django.dispatch import receiver #Connects functions to signals
from django.contrib.auth.models import User
from .models import Profile


@receiver(post_save, sender=User) #The model class(User) that sent the signal
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    
    
#User creates a new acc
#Django calls post_save signal after saving the User
#Signal 1 detects created=True and creates a Profile
#Signal 2 runs and saves the newly created Profile