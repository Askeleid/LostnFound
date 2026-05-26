from django import forms
from .models import Item, Claim
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

INPUT   = "w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
TEXTAREA = "w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
SELECT  = "w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
FILE    = "text-sm text-gray-600 file:mr-3 file:py-1 file:px-3 file:rounded file:border-0 file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"


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
        # password1 and password2 come from UserCreationForm, style them here
        self.fields['password1'].widget.attrs.update({'class': INPUT})
        self.fields['password2'].widget.attrs.update({'class': INPUT})


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        exclude = ['user', 'status', 'date_posted', 'updated_at', 'image_embedding', 'text_embedding']
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
            'message':     'Message',
            'claim_image': 'Optional Image',
        }