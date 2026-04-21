from django import forms
from .models import Resolution

class ResolutionForm(forms.ModelForm):
    class Meta:
        model = Resolution
        fields = ['title', 'question', 'context']
        widgets = {
            'context': forms.Textarea(attrs={'rows': 4}),
        }