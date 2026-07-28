from django import forms
from .models import ArticleComment

class ArticleCommentForm(forms.ModelForm):
    class Meta:
        model = ArticleComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control rounded-3',
                'rows': 3,
                'placeholder': 'O que você achou desta notícia/artigo? Deixe seu comentário...',
                'required': True
            })
        }
