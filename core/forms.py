from django import forms
from .models import Item, Claim

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        exclude = ['user', 'status', 'date_posted', 'updated_at']

class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = ['message', 'claim_image']  # includes optional image
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write your claim message here...'
            }),
        }
        labels = {
            'message': 'Message',
            'claim_image': 'Optional Image',
        }