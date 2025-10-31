from django import forms
from .models import MinigameLevel

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
