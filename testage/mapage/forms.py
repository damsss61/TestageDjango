from django import forms
from .models import Resolution
from .models import Comment

class ResolutionForm(forms.ModelForm):
    class Meta:
        model = Resolution
        fields = ['title', 'question', 'context']
        widgets = {
            'context': forms.Textarea(attrs={'rows': 4}),
        }
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ajoutez votre commentaire ici...'}),
        }