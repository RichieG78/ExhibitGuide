from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm #Inheritance Relationship

from exhibits.models import Exhibit

from .models import GalleryInquiry, SavedCollection, UserProfile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].disabled = True


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['firstname', 'lastname', 'phone', 'bio']


class SavedCollectionForm(forms.ModelForm):
    exhibits = forms.ModelMultipleChoiceField(
        queryset=Exhibit.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = SavedCollection
        fields = ['name', 'notes', 'exhibits']


class GalleryInquiryForm(forms.ModelForm):
    class Meta:
        model = GalleryInquiry
        fields = ['exhibit', 'message']