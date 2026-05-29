import numpy as np
import logging
from typing import cast

logger = logging.getLogger("ai_pipeline")

_image_model = None
_text_model = None
_transform = None  # lazy too

def get_image_model():
    global _image_model
    if _image_model is None:
        import torch
        import torchvision.models as models
        model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
        _image_model = model.features
        _image_model.eval()
    return _image_model

def get_transform():
    global _transform
    if _transform is None:
        import torchvision.transforms as transforms
        _transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ColorJitter(brightness=0.1, contrast=0.1),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    return _transform

def get_text_model():
    global _text_model
    if _text_model is None:
        from sentence_transformers import SentenceTransformer
        _text_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _text_model

def get_image_embedding(image_path):
    try:
        if not image_path:
            return None
        import torch
        from PIL import Image
        pil_image = Image.open(image_path)
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert('RGB')
        image = get_transform()(pil_image)
        assert isinstance(image, torch.Tensor)
        image = image.unsqueeze(0)
        model = get_image_model()
        with torch.no_grad():
            features = model(image)
        embedding = torch.nn.functional.adaptive_avg_pool2d(features, (1, 1))
        embedding = embedding.squeeze().flatten().cpu().numpy()
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return None
        return (embedding / norm).tolist()
    except Exception as e:
        logger.warning(f"[IMAGE_EMBEDDING_FAILED] path={image_path} error={str(e)}")
        return None

def get_text_embedding(text):
    try:
        model = get_text_model()
        embedding = model.encode(text)
        return embedding.tolist()
    except Exception as e:
        logger.warning(f"[TEXT_EMBEDDING_FAILED] error={str(e)} text={text[:50]}")
        return None
    
def build_text(item):
    parts = []
    parts.append(f"{item.title}.")
    if item.description:
        parts.append(item.description)
    if item.location:
        parts.append(f"It was lost or found at {item.location}.")
    return " ".join(parts)
    
# -----------------------------
# Similarity functions
# -----------------------------

def cosine_similarity(a, b):
    if not a or not b:
        return None

    a = np.array(a)
    b = np.array(b)

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return None

    return float(np.dot(a, b) / (norm_a * norm_b))


def combined_similarity(item_a, item_b, alpha=0.5):
    img_sim = cosine_similarity(
        item_a.get("image_embedding"),
        item_b.get("image_embedding")
    )

    text_sim = cosine_similarity(
        item_a.get("text_embedding"),
        item_b.get("text_embedding")
    )
    
    if img_sim is None and text_sim is None:
        return None
    
    if img_sim is None:
        return {
            "score": text_sim,
            "cv_score": None,
            "nlp_score": text_sim,
            "disagreement": 0,
            "explanation": {
                "mode": "NLP_ONLY"
            }
        }

    if text_sim is None:
        return {
            "score": img_sim,
            "cv_score": img_sim,
            "nlp_score": None,
            "disagreement": 0,
            "explanation": {
                "mode": "CV_ONLY"
            }
        }

    base = (alpha * img_sim) + ((1 - alpha) * text_sim)
    
    #disagreement handling
    diff = abs(img_sim - text_sim) #Disagreement penalty
    penalty = diff * 0.3
    
    score = base - penalty #prevents false positives
    #Top-K explanation system
    return {
        "score": score,
        "cv_score": img_sim,
        "nlp_score": text_sim,
        "disagreement": abs(img_sim - text_sim),
        "explanation": {
            "cv_contribution": alpha * img_sim,
            "nlp_contribution": (1 - alpha) * text_sim,
            "penalty": penalty
    }
}
                                





# Current CV pipeline:
#     Image → EfficientNet-B0 → feature map
#             ↓
#     global average pooling
#             ↓
#     normalized embedding vector
#             ↓
#     cosine similarity