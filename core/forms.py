from django import forms
from .models import Item, Claim
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        ]

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        exclude = ['user', 'status', 'date_posted', 'updated_at']
        fields = '__all__'
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}),
        }

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