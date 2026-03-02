from django.contrib import admin
from .models import Profile, Category, Item, Claim

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'trust_score', 'created_at')
    search_fields = ('user__username', 'phone_number')
    readonly_fields = ('trust_score', 'created_at')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'item_type', 'status', 'category', 'user', 'event_date', 'date_posted')
    list_filter = ('item_type', 'status', 'category')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('date_posted', 'updated_at')
    raw_id_fields = ('user',)
    ordering = ('-date_posted',)

@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('item', 'claimer', 'status', 'confidence_score', 'created_at', 'reviewed_at')
    list_filter = ('status',)
    search_fields = ('item__title', 'claimer__username', 'message')
    readonly_fields = ('confidence_score', 'created_at', 'reviewed_at')
    raw_id_fields = ('item', 'claimer')
    ordering = ('-created_at',)