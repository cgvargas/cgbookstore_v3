from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from accounts.models import UserProfile
from core.models import Category
from accounts.models import UserProfile, BookReview
from accounts.models import UserProfile, BookReview


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="E-mail")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)


class UserProfileForm(forms.ModelForm):
    """Form para editar perfil do usuário."""
    
    # Campos do modelo User (não do UserProfile)
    first_name = forms.CharField(
        max_length=30,
        required=False,
        label='Nome',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu primeiro nome'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        label='Sobrenome',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu sobrenome'
        })
    )

    class Meta:
        model = UserProfile
        fields = [
            'bio',
            'favorite_genre',
            'theme_preference',
            'reading_goal_year',
            'is_profile_public',
            'allow_followers',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Conte um pouco sobre você e seus gostos literários...',
                'maxlength': 150
            }),
            'favorite_genre': forms.Select(attrs={
                'class': 'form-select'
            }),
            'theme_preference': forms.Select(attrs={
                'class': 'form-select'
            }),
            'reading_goal_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 365
            }),
            'is_profile_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'allow_followers': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'bio': 'Bio Literária',
            'favorite_genre': 'Gênero Favorito',
            'theme_preference': 'Tema Visual da Biblioteca',
            'reading_goal_year': 'Meta de Leitura (livros/ano)',
            'is_profile_public': 'Perfil Público',
            'allow_followers': 'Permitir Seguidores',
        }
        help_texts = {
            'bio': 'Máximo de 150 caracteres',
            'reading_goal_year': 'Quantos livros você pretende ler este ano?',
            'is_profile_public': 'Permitir que outros usuários vejam seu perfil e estatísticas',
            'allow_followers': 'Permitir que outros usuários te sigam',
        }
    
    def __init__(self, *args, **kwargs):
        """Inicializa o form com dados do User."""
        super().__init__(*args, **kwargs)
        
        # Carregar valores atuais do User
        if self.instance and self.instance.user:
            user = self.instance.user
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
    
    def save(self, commit=True):
        """Salva tanto UserProfile quanto User."""
        profile = super().save(commit=False)
        
        # Salvar dados do User
        if profile.user:
            profile.user.first_name = self.cleaned_data.get('first_name', '')
            profile.user.last_name = self.cleaned_data.get('last_name', '')
            if commit:
                profile.user.save()
        
        if commit:
            profile.save()
        
        return profile


class BookReviewForm(forms.ModelForm):
    """Formulário para avaliação e resenha de livros."""
    class Meta:
        model = BookReview
        fields = ['rating', 'title', 'review_text', 'contains_spoilers', 'would_recommend']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.0',
                'max': '5.0',
                'step': '0.1',
                'placeholder': 'Ex: 4.5',
                'required': True
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Resuma sua avaliação em uma frase (opcional)'
            }),
            'review_text': forms.Textarea(attrs={
                'class': 'form-control text-white',
                'rows': 4,
                'placeholder': 'O que você achou deste livro? (opcional)'
            }),
            'contains_spoilers': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'would_recommend': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'rating': 'Avaliação (0.0 a 5.0)',
            'title': 'Título da Resenha',
            'review_text': 'Resenha',
            'contains_spoilers': 'Contém Spoilers',
            'would_recommend': 'Eu recomendo este livro',
        }


