from .embeddings import cosine_similarity


def match_items(source_item, candidate_items, alpha=0.5):
    results = []
    
    if not source_item.image_embedding or not source_item.text_embedding:
        return []


    for item in candidate_items:
        if source_item.item_type == item.item_type: #Enforces Lost <-> Found pairing
            continue
        if item.user == source_item.user:
            continue
        
        if not item.image_embedding or not item.text_embedding:
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
        final_score = base_score + category_boost + location_boost
        

        results.append({
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