from django.db.models.signals import post_save #signal sent after save() is called
from django.dispatch import receiver #Connects functions to signals
from django.contrib.auth.models import User
from .models import Profile
from .models import Item
from core.utils.embeddings import get_image_embedding, build_text, get_text_embedding


@receiver(post_save, sender=User) #The model class(User) that sent the signal
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    
@receiver(post_save, sender=Item)
def generate_embeddings(sender, instance, created, **kwargs):
    if not created:
        return

    image_emb = None
    text_emb = None

    if instance.image:
        image_emb = get_image_embedding(instance.image.path)

    if instance.description:
        text = build_text(instance)
        text_emb = get_text_embedding(text)

    Item.objects.filter(pk=instance.pk).update(
        image_embedding=image_emb,
        text_embedding=text_emb
    )   
    
#User creates a new acc
#Django calls post_save signal after saving the User
#Signal 1 detects created=True and creates a Profile
#Signal 2 runs and saves the newly created Profile
