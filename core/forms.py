from django import forms
from .models import Item
from .models import Claim

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        exclude = ['user', 'status', 'date_posted', 'updated_at']
        
class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = ['message']