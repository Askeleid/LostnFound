import csv
from core.models import ItemMatch

def export_training_data(filepath='training_data.csv'):

    matches = ItemMatch.objects.all()

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        writer.writerow([
            'cv_score',
            'nlp_score',
            'final_score',
            'category_match',
            'location_match',
            'status',
            'label'
        ])

        for m in matches:
            if m.cv_score is None and m.nlp_score is None:
                continue

            label = 1 if (
                m.user_feedback == "HELPFUL"
                or m.status == "ACCEPTED"
            ) else 0

            writer.writerow([
                m.cv_score or 0,
                m.nlp_score or 0,
                m.score or 0,
                int(m.category_match),
                int(m.location_match),
                m.status,
                label
            ])

    print("Training dataset exported.")