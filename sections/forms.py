from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import MinigameLevel

class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form that includes first_name and last_name"""
    first_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='Optional.',
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        help_text='Optional.',
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
        return user

class MinigameLevelForm(forms.ModelForm):
    class Meta:
        model = MinigameLevel
        fields = ['image1', 'image2', 'image3', 'image4', 'answer']
        widgets = {
            'image1': forms.FileInput(attrs={'accept': 'image/*'}),
            'image2': forms.FileInput(attrs={'accept': 'image/*'}),
            'image3': forms.FileInput(attrs={'accept': 'image/*'}),
            'image4': forms.FileInput(attrs={'accept': 'image/*'}),
            'answer': forms.TextInput(attrs={'placeholder': 'Enter the correct answer'}),
        }
