from django.db import migrations

def add_categories(apps, schema_editor):
    Category = apps.get_model('core', 'Category')
    categories = [
        'Wallet',
        'Bag',
        'Phone',
        'Laptop',
        'Keys',
        'ID Card',
        'Book',
        'Clothing',
        'Accessories',
        'Headphones',
        'Charger',
        'Stationery',
        'Water Bottle',
        'Umbrella',
        'Other'
    ]
    for name in categories:
        Category.objects.get_or_create(name=name)

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),  # make sure this points to your initial migration
    ]

    operations = [
        migrations.RunPython(add_categories),
    ]