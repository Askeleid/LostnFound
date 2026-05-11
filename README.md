# Lost & Found System (Intra-University)

A Django web application for reporting and recovering lost and found items within a university, with an AI-powered matching pipeline.

---

## Tech Stack

- **Backend:** Django 5.2
- **Database:** PostgreSQL 18
- **Image Embeddings:** EfficientNet-B0 (PyTorch)
- **Text Embeddings:** SentenceTransformer MiniLM-L6-v2
- **Similarity:** NumPy cosine similarity

---

## Features

- Lost/Found item posting with image upload
- Claim submission, approval, and rejection with email notifications
- In-app notification system
- AI match suggestions using image + text embeddings
- Feedback-aware ranking — adjusts image/text weight per category based on accepted matches
- Staff-only dataset export (CSV) for future model training

---

## AI Pipeline

1. Item is posted → EfficientNet-B0 and MiniLM-L6-v2 generate image and text embeddings
2. Matching runs → cosine similarity scored, category and location boosts applied
3. User accepts or rejects suggestions → feedback stored per match
4. `get_learned_alpha()` adjusts CV/NLP weighting per category from historical feedback
5. Reviewed matches are score-frozen to preserve training data integrity
6. Staff exports labeled dataset (CSV) for future fine-tuning

---

## Models

| Model | Purpose |
|---|---|
| `Profile` | Extends User with phone number and trust score |
| `Item` | Lost/Found postings with dual embeddings |
| `Claim` | Claim lifecycle with atomic approval |
| `ItemMatch` | Match pairs with scores, boosts, feedback, and training labels |
| `Notification` | In-app event notifications |

---

## Planned

- Fine-tune ranking model on exported dataset
- Trust score and moderation system
- Semantic location matching