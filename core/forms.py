from django import forms
from .models import Item, Claim
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

INPUT = "tron-input"
TEXTAREA = "tron-input"
SELECT = "tron-input"
FILE = "tron-input"


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': INPUT}))
    last_name  = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': INPUT}))
    email      = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': INPUT}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': INPUT}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password1'].widget.attrs.update({'class': INPUT})
        self.fields['password2'].widget.attrs.update({'class': INPUT})
        
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'tron-input'
    }))

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'tron-input'
    }))


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        exclude = [
            'user',
            'status',
            'date_posted',
            'updated_at',
            'image_embedding',
            'text_embedding'
        ]

        widgets = {
            'title':       forms.TextInput(attrs={'class': INPUT}),
            'description': forms.Textarea(attrs={'class': TEXTAREA, 'rows': 4}),
            'category':    forms.Select(attrs={'class': SELECT}),
            'item_type':   forms.Select(attrs={'class': SELECT}),
            'location':    forms.TextInput(attrs={'class': INPUT}),
            'event_date':  forms.DateInput(attrs={'class': INPUT, 'type': 'date'}),
            'image':       forms.ClearableFileInput(attrs={'class': FILE}),
        }


class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = ['message', 'claim_image']

        widgets = {
            'message': forms.Textarea(attrs={
                'class': TEXTAREA,
                'rows': 4,
                'placeholder': 'Write your claim message here...'
            }),
            'claim_image': forms.ClearableFileInput(attrs={'class': FILE}),
        }

        labels = {
            'message': 'Message',
            'claim_image': 'Optional Image',
        }