from django import forms
from .models import Resolution, Comment, Vote
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
class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['judgment_for', 'judgment_against']
        widgets = {
            'judgment_for': forms.RadioSelect,
            'judgment_against': forms.RadioSelect,
        }
        labels = {
            'judgment_for': 'Jugement pour cette résolution :',
            'judgment_against': 'Jugement contre cette résolution :',
        }