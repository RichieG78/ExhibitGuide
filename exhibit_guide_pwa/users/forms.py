"""Forms used by registration, profiles, collections, and gallery inquiries."""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from exhibits.models import Exhibit

from .models import GalleryInquiry, SavedCollection, UserProfile

class UserRegisterForm(UserCreationForm):
    """Signup form that asks for email in addition to Django's default fields."""
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserAccountForm(forms.ModelForm):
    """Form for the account-level fields stored on Django's built-in User model."""
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class UserProfileForm(forms.ModelForm):
    """Form for collector details used in the profile page and inquiries."""
    class Meta:
        model = UserProfile
        fields = ['image', 'firstname', 'lastname', 'phone', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }


class SavedCollectionForm(forms.ModelForm):
    """Form that creates or edits a user-defined collection of exhibits."""
    exhibits = forms.ModelMultipleChoiceField(
        queryset=Exhibit.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = SavedCollection
        fields = ['name', 'notes', 'exhibits']


class GalleryInquiryForm(forms.ModelForm):
    """Simple form that sends a message to the gallery about one exhibit."""
    class Meta:
        model = GalleryInquiry
        fields = ['exhibit', 'message']

