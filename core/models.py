from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q #For complex db queries that needs logical operators
from django.utils import timezone
from django.db import transaction #Ensures atomicity
from django.core.exceptions import ValidationError, PermissionDenied
from core.utils.embeddings import get_image_embedding, get_text_embedding


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) #One user = One profile
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

class ItemQuerySet(models.QuerySet["Item"]): #Defining custom query set
    def open(self) -> "ItemQuerySet":
        return self.filter(status='OPEN')

    def lost(self) -> "ItemQuerySet":
        return self.filter(item_type='LOST')

    def found(self) -> "ItemQuerySet":
        return self.filter(item_type='FOUND') #Can do chainable methods e.g. Item.objects.open().lost()

class ItemManager(models.Manager["Item"]): #passes calls to the custom query set
    def get_queryset(self) -> ItemQuerySet:
        return ItemQuerySet(self.model, using=self._db)

    def open(self) -> ItemQuerySet:
        return self.get_queryset().open()

    def lost(self) -> ItemQuerySet:
        return self.get_queryset().lost()

    def found(self) -> ItemQuerySet:
        return self.get_queryset().found()

class Item(models.Model): #(db_value, display_value) format for django admin
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
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    title = models.CharField(max_length=255)
    description = models.TextField()

    image = models.ImageField(upload_to='item_images/', null=True, blank=True)

    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)
    location = models.CharField(max_length=255)

    event_date = models.DateField(null=True, blank=True)  #actual lost/found date
    date_posted = models.DateTimeField(auto_now_add=True) #Set once when object is created
    updated_at = models.DateTimeField(auto_now=True) #Updates everytime object is saved

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')

    image_embedding = models.JSONField(null=True, blank=True)
    text_embedding = models.JSONField(null=True, blank=True)
    objects = ItemManager()  # type: ignore[assignment]

    class Meta: #provides metadata (config options)
        indexes = [
            models.Index(fields=['item_type']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['date_posted']),
        ] #speeds up queries on these fields

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
        unique_together = ('item', 'claimer') #Prevents duplicate claims on the same item
        constraints = [
            models.UniqueConstraint(
                fields=['item'],
                condition=Q(status='APPROVED'), #Only one approved claim per item
                name='unique_approved_claim_per_item'
            )
        ]
    
    def clean(self):
        if not self.item_id:
            return
        if self.item.user == self.claimer:
            raise ValidationError("You cannot claim your own item.")
        
        if Claim.objects.filter(item=self.item, claimer=self.claimer).exclude(pk=self.pk).exists():
            raise ValidationError("You have already claimed this item.")
        
        if self.status == 'APPROVED':
            if Claim.objects.filter(item=self.item, status='APPROVED').exclude(pk=self.pk).exists():
                raise ValidationError("This item already has an approved claim.")

    def __str__(self):
        return f"Claim by {self.claimer.username} on {self.item.title}"
    
    def save(self, *args, **kwargs):
        self.full_clean(exclude=['item'] if not self.item_id else [])
        super().save(*args, **kwargs)
    
    @transaction.atomic
    def approve(self, acting_user):
        if self.item.user != acting_user:
            raise PermissionDenied("Only the item owner can approve this claim.")

        if self.status != 'PENDING':
            raise ValueError("Claim already processed")

        self.status = 'APPROVED'
        self.reviewed_at = timezone.now()
        self.save()

        self.item.status = 'CLOSED'
        self.item.save()
        
    def reject(self, acting_user):
        if self.item.user != acting_user:
            raise PermissionDenied("Only the item owner can reject this claim.")

        if self.status != 'PENDING':
            raise ValueError("Claim already processed")

        self.status = 'REJECTED'
        self.reviewed_at = timezone.now()
        self.save()        
# One approved claim per item (database constraint)
# Claim status changes are atomic (transaction)
# Approving a claim automatically closes the item
# Items can have multiple pending claims, but only one approved

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"
    
    

class ItemMatch(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]

    source_item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='source_matches'
    )

    matched_item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='candidate_matches'
    )

    score = models.FloatField()

    cv_score = models.FloatField(null=True, blank=True)
    nlp_score = models.FloatField(null=True, blank=True)

    category_boost = models.FloatField(default=0)
    location_boost = models.FloatField(default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    user_feedback = models.CharField(
        max_length=20,
        choices=[
            ('HELPFUL', 'Helpful'),
            ('NOT_HELPFUL', 'Not Helpful'),
            ('IGNORED', 'Ignored'),
        ],
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('source_item', 'matched_item')
        ordering = ['-score']

    def __str__(self):
        return f"{self.source_item.title} → {self.matched_item.title} ({self.score:.2f})"