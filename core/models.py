from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    trust_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Item(models.Model):
    ITEM_TYPE_CHOICES = [
        ('LOST', 'Lost'),
        ('FOUND', 'Found')
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLAIMED', 'Claimed'),
        ('CLOSED', 'Closed'),
        ('REPORTED', 'Reported'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="items")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    title = models.CharField(max_length=255)
    description = models.TextField()

    image = models.ImageField(upload_to='item_images/', null=True, blank=True)

    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)
    location = models.CharField(max_length=255)

    event_date = models.DateField(null=True, blank=True)  # actual lost/found date
    date_posted = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')

    embedding_vector = models.JSONField(null=True, blank=True)  # future AI embeddings

    class Meta:
        indexes = [
            models.Index(fields=['item_type']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['date_posted']),
        ]

    def __str__(self):
        return f"{self.title} ({self.item_type})"


class Claim(models.Model):
    CLAIM_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected')
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="claims")
    claimer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="claims")

    message = models.TextField()
    claim_image = models.ImageField(upload_to='claim_images/', null=True, blank=True)

    confidence_score = models.FloatField(null=True, blank=True)  # future AI comparison

    status = models.CharField(max_length=10, choices=CLAIM_STATUS_CHOICES, default='PENDING')

    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('item', 'claimer')

    def __str__(self):
        return f"Claim by {self.claimer.username} on {self.item.title}"