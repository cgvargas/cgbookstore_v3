"""
Formulários para o módulo de autores emergentes.
"""

from django import forms
from .models import AuthorBook, Chapter


class AuthorBookForm(forms.ModelForm):
    """Formulário para criar/editar livros de autores."""

    class Meta:
        model = AuthorBook
        fields = [
            'title', 'synopsis', 'genre', 'cover_image',
            'target_audience', 'tags', 'content_warning', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o título do livro'
            }),
            'synopsis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Escreva uma sinopse envolvente para atrair leitores...'
            }),
            'genre': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'target_audience': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'romance, fantasia, aventura (separados por vírgula)'
            }),
            'content_warning': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Avisos sobre conteúdo sensível (opcional)'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'title': 'Título',
            'synopsis': 'Sinopse',
            'genre': 'Gênero',
            'cover_image': 'Capa do Livro',
            'target_audience': 'Público-Alvo',
            'tags': 'Tags',
            'content_warning': 'Avisos de Conteúdo',
            'status': 'Status',
        }


class ChapterForm(forms.ModelForm):
    """Formulário para criar/editar capítulos."""

    class Meta:
        model = Chapter
        fields = ['title', 'content', 'is_published', 'author_notes']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Capítulo 1: O Início'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 20,
                'placeholder': 'Escreva o conteúdo do capítulo aqui...',
                'style': 'font-family: "Georgia", serif; font-size: 16px;'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'author_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas do autor (opcional)'
            }),
        }
        labels = {
            'title': 'Título do Capítulo',
            'content': 'Conteúdo',
            'is_published': 'Publicar este capítulo',
            'author_notes': 'Notas do Autor',
        }
