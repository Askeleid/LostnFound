from .embeddings import cosine_similarity
from core.models import ItemMatch
import logging

logger = logging.getLogger("ai_pipeline")

def get_learned_alpha(category):
    accepted = list(ItemMatch.objects.filter(
        status='ACCEPTED',
        source_item__category=category,
        cv_score__isnull=False,
        nlp_score__isnull=False,
    ))

    if len(accepted) < 10:
        return 0.5  # not enough data, use equal weight

    avg_cv  = sum(m.cv_score  for m in accepted if m.cv_score is not None) / len(accepted)
    avg_nlp = sum(m.nlp_score for m in accepted if m.nlp_score is not None) / len(accepted)

    total = avg_cv + avg_nlp
    if total == 0:
        return 0.5

    return avg_cv / total  # how much image matters vs text for this category

def match_items(source_item, candidate_items):
    results = []
    
    
    
    if not source_item.text_embedding: #!!!!
        logger.warning(
            f"[MATCH_SKIPPED_SOURCE] item_id={source_item.id} reason=missing_embeddings"
        )
        return []

    alpha = get_learned_alpha(source_item.category)
    
    for item in candidate_items:
        if source_item.item_type == item.item_type: #Enforces Lost <-> Found pairing
            continue
        if item.user == source_item.user:
            continue
        if source_item.id == item.id:
            continue
        
        if not item.text_embedding: #!!!
            logger.info(
                f"[MATCH_SKIPPED_CANDIDATE] item_id={item.id} reason=missing_embeddings"
            )
            continue

        # image similarity
        img_sim = cosine_similarity(
            source_item.image_embedding,
            item.image_embedding
        )

        # text similarity
        text_sim = cosine_similarity(
            source_item.text_embedding,
            item.text_embedding
        )
        
        if img_sim is None and text_sim is None:
            continue
        
        # fallback handling
        if img_sim is None:
            img_sim = 0

        if text_sim is None:
            text_sim = 0
        
        if img_sim == 0 and text_sim != 0:
            base_score = text_sim
        elif text_sim == 0 and img_sim != 0:
            base_score = img_sim
        else:
            base_score = alpha * img_sim + (1 - alpha) * text_sim
        #Category boost
        category_boost = 0.1 if source_item.category == item.category else 0
        #Location boost
        location_boost = 0
        if source_item.location and item.location:
            if source_item.location.lower() in item.location.lower():
                location_boost = 0.1

        # final score -> Image+text similarity+Category & location relevance
        final_score = min(1.0, (base_score + category_boost + location_boost))
        

        match_obj, created = ItemMatch.objects.get_or_create(
            source_item=source_item,
            matched_item=item,
            defaults={
                "score": final_score,
                "cv_score": img_sim,
                "nlp_score": text_sim,
                "category_boost": category_boost,
                "location_boost": location_boost,
                "category_match": source_item.category == item.category,
                "location_match": location_boost > 0,
                "status": "PENDING",
            }
        )
        
        if not created and match_obj.status == 'PENDING':
            match_obj.score = final_score
            match_obj.cv_score = img_sim
            match_obj.nlp_score = text_sim
            match_obj.category_boost = category_boost
            match_obj.location_boost = location_boost
            match_obj.category_match = source_item.category == item.category
            match_obj.location_match = location_boost > 0
            match_obj.save()

        results.append({
            "match_obj": match_obj,
            "item": item,
            "score": final_score,
            "base_score": base_score,
            "category_boost": category_boost,
            "location_boost": location_boost,
            "img_sim": img_sim,
            "text_sim": text_sim,
            "alpha": alpha
        })

    # sort best matches first
    results.sort(key=lambda x: x["score"], reverse=True)

    return results