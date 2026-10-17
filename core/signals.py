import threading
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import transaction, close_old_connections
from .models import Profile, Item

logger = logging.getLogger("ai_pipeline")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


def _process_item_ai_async(item_id):
    """
    Runs in a background thread:
    1. Computes image and text embeddings.
    2. Saves embeddings to the Item.
    3. Runs candidate matching and persists ItemMatch records.
    """
    close_old_connections()
    try:
        from core.utils.embeddings import get_image_embedding, build_text, get_text_embedding
        from core.utils.matching import process_item_matches

        try:
            item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            return

        image_emb = None
        text_emb = None

        if item.image:
            try:
                image_emb = get_image_embedding(item.image.path)
            except Exception as e:
                logger.warning(f"[IMAGE_EMBEDDING_FAILED] item_id={item.pk} error={e}")

        if item.description:
            try:
                text = build_text(item)
                text_emb = get_text_embedding(text)
            except Exception as e:
                logger.warning(f"[TEXT_EMBEDDING_FAILED] item_id={item.pk} error={e}")

        Item.objects.filter(pk=item.pk).update(
            image_embedding=image_emb,
            text_embedding=text_emb
        )
        item.refresh_from_db()

        # Generate matches for this new item in the background
        process_item_matches(item)
        logger.info(f"[AI_PIPELINE_COMPLETE] item_id={item.pk}")

    except Exception as e:
        logger.error(f"[AI_PIPELINE_ERROR] item_id={item_id} error={e}", exc_info=True)
    finally:
        close_old_connections()


@receiver(post_save, sender=Item)
def generate_embeddings(sender, instance, created, **kwargs):
    if not created:
        return

    # Trigger async thread after database transaction commits
    transaction.on_commit(
        lambda: threading.Thread(
            target=_process_item_ai_async,
            args=(instance.pk,),
            daemon=True
        ).start()
    )
