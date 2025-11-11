from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from accounts.models import UserProfile
from core.models import Category


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="E-mail")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)


class UserProfileForm(forms.ModelForm):
    """Form para editar perfil do usuário."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ SEGURANÇA: Filtrar temas premium para usuários free
        if self.instance and self.instance.pk:
            if not self.instance.is_premium_active():
                # Lista de temas premium (deve corresponder aos temas em user_profile.py)
                premium_themes = [
                    'scifi', 'horror', 'mystery', 'biography', 'poetry',
                    'adventure', 'thriller', 'historical', 'selfhelp',
                    'philosophy', 'dystopian', 'contemporary'
                ]

                # Filtrar choices para remover temas premium
                from accounts.models.user_profile import THEME_CHOICES
                free_choices = [
                    choice for choice in THEME_CHOICES
                    if choice[0] not in premium_themes
                ]

                # Atualizar opções do campo
                self.fields['theme_preference'].choices = free_choices

    def clean_theme_preference(self):
        """✅ SEGURANÇA: Validar que usuários free não selecionem temas premium."""
        theme = self.cleaned_data.get('theme_preference')

        # Lista de temas premium
        premium_themes = [
            'scifi', 'horror', 'mystery', 'biography', 'poetry',
            'adventure', 'thriller', 'historical', 'selfhelp',
            'philosophy', 'dystopian', 'contemporary'
        ]

        # Verificar se é tema premium e se usuário não é premium
        if theme in premium_themes:
            if not self.instance.is_premium_active():
                raise forms.ValidationError(
                    "Este tema é exclusivo para membros Premium. "
                    "Assine o plano Premium para desbloquear todos os temas!"
                )

        return theme

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
