"""
Formulários para o módulo de autores emergentes.
"""

from django import forms
from django.core.exceptions import ValidationError
from datetime import date
import re
from .models import EmergingAuthor, AuthorBook, Chapter, AuthorTermsOfService


class EmergingAuthorRegistrationForm(forms.ModelForm):
    """
    Formulário completo de cadastro de autor emergente
    com validações rigorosas e aceite de termos
    """

    # Campo adicional para confirmar aceite dos termos
    accept_terms = forms.BooleanField(
        required=True,
        label='Li e aceito os Termos de Responsabilidade',
        error_messages={
            'required': 'Você deve aceitar os termos para continuar.'
        }
    )

    # Campos com widgets customizados
    writing_genres = forms.MultipleChoiceField(
        choices=[
            ('fiction', 'Ficção'),
            ('romance', 'Romance'),
            ('fantasy', 'Fantasia'),
            ('scifi', 'Ficção Científica'),
            ('mystery', 'Mistério'),
            ('thriller', 'Thriller'),
            ('horror', 'Terror'),
            ('adventure', 'Aventura'),
            ('historical', 'Histórico'),
            ('biography', 'Biografia'),
            ('poetry', 'Poesia'),
            ('self_help', 'Autoajuda'),
            ('young_adult', 'Jovem Adulto'),
            ('children', 'Infantil'),
            ('other', 'Outro'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Gêneros que você escreve'
    )

    class Meta:
        model = EmergingAuthor
        fields = [
            'full_name', 'cpf', 'birth_date', 'phone',
            'cep', 'street', 'number', 'complement', 'neighborhood', 'city', 'state',
            'bio', 'literary_experience', 'writing_genres', 'photo',
            'identity_document', 'cpf_document', 'proof_of_address',
            'website', 'twitter', 'instagram', 'facebook', 'linkedin',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo como aparecerá nas publicações',
                'required': True
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00',
                'maxlength': '14',
                'required': True,
                'data-mask': '000.000.000-00'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000',
                'required': True,
                'data-mask': '(00) 00000-0000'
            }),
            'cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000',
                'maxlength': '9',
                'required': True,
                'data-mask': '00000-000',
                'id': 'cep-input'
            }),
            'street': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rua, Avenida, etc.',
                'required': True,
                'id': 'street-input'
            }),
            'number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número',
                'required': True
            }),
            'complement': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apto, Bloco, etc. (opcional)'
            }),
            'neighborhood': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bairro',
                'required': True,
                'id': 'neighborhood-input'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade',
                'required': True,
                'id': 'city-input'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'UF (ex: SP, RJ)',
                'maxlength': '2',
                'required': True,
                'id': 'state-input',
                'style': 'text-transform: uppercase;'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Conte sua história como escritor, suas motivações e objetivos...',
                'maxlength': '2000',
                'required': True
            }),
            'literary_experience': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Prêmios, publicações anteriores, cursos, oficinas, etc.',
                'maxlength': '1000'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'required': True
            }),
            'identity_document': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf',
                'required': True
            }),
            'cpf_document': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'proof_of_address': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf',
                'required': True
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://seu-site.com'
            }),
            'twitter': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '@seu_usuario'
            }),
            'instagram': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '@seu_usuario'
            }),
            'facebook': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'facebook.com/seu.perfil'
            }),
            'linkedin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'linkedin.com/in/seu-perfil'
            }),
        }
        labels = {
            'full_name': 'Nome Completo *',
            'cpf': 'CPF *',
            'birth_date': 'Data de Nascimento *',
            'phone': 'Telefone/Celular *',
            'cep': 'CEP *',
            'street': 'Rua/Avenida *',
            'number': 'Número *',
            'complement': 'Complemento',
            'neighborhood': 'Bairro *',
            'city': 'Cidade *',
            'state': 'Estado (UF) *',
            'bio': 'Biografia Literária *',
            'literary_experience': 'Experiência Literária',
            'photo': 'Foto Profissional *',
            'identity_document': 'Documento de Identidade (RG ou CNH) *',
            'cpf_document': 'Comprovante de CPF',
            'proof_of_address': 'Comprovante de Residência *',
            'website': 'Website Pessoal',
            'twitter': 'Twitter/X',
            'instagram': 'Instagram',
            'facebook': 'Facebook',
            'linkedin': 'LinkedIn',
        }

    def clean_cpf(self):
        """Valida CPF com dígitos verificadores"""
        cpf = self.cleaned_data.get('cpf', '')

        # Remove caracteres não numéricos
        cpf_numbers = re.sub(r'[^0-9]', '', cpf)

        # Verifica se tem 11 dígitos
        if len(cpf_numbers) != 11:
            raise ValidationError('CPF deve conter 11 dígitos.')

        # Verifica se todos os dígitos são iguais
        if cpf_numbers == cpf_numbers[0] * 11:
            raise ValidationError('CPF inválido.')

        # Validação dos dígitos verificadores
        def calculate_digit(cpf_partial):
            total = sum((len(cpf_partial) + 1 - i) * int(digit) for i, digit in enumerate(cpf_partial))
            remainder = total % 11
            return '0' if remainder < 2 else str(11 - remainder)

        first_digit = calculate_digit(cpf_numbers[:9])
        second_digit = calculate_digit(cpf_numbers[:10])

        if cpf_numbers[9] != first_digit or cpf_numbers[10] != second_digit:
            raise ValidationError('CPF inválido. Verifique os dígitos.')

        # Verifica se CPF já existe
        if EmergingAuthor.objects.filter(cpf=cpf_numbers).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise ValidationError('Este CPF já está cadastrado no sistema.')

        return cpf_numbers

    def clean_birth_date(self):
        """Valida se o autor tem 18 anos ou mais"""
        birth_date = self.cleaned_data.get('birth_date')

        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

            if age < 18:
                raise ValidationError(f'Você deve ter no mínimo 18 anos. Idade atual: {age} anos.')

            if age > 120:
                raise ValidationError('Data de nascimento inválida.')

        return birth_date

    def clean_phone(self):
        """Valida formato do telefone"""
        phone = self.cleaned_data.get('phone', '')
        phone_numbers = re.sub(r'[^0-9]', '', phone)

        if len(phone_numbers) not in [10, 11]:
            raise ValidationError('Telefone deve ter 10 ou 11 dígitos.')

        return phone

    def clean_cep(self):
        """Valida formato do CEP"""
        cep = self.cleaned_data.get('cep', '')
        cep_numbers = re.sub(r'[^0-9]', '', cep)

        if len(cep_numbers) != 8:
            raise ValidationError('CEP deve conter 8 dígitos.')

        return cep

    def clean_state(self):
        """Valida UF do estado"""
        state = self.cleaned_data.get('state', '').upper()

        valid_states = [
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
            'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
            'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ]

        if state not in valid_states:
            raise ValidationError('UF inválida. Use a sigla do estado (ex: SP, RJ, MG).')

        return state

    def clean_photo(self):
        """Valida tamanho e tipo da foto"""
        photo = self.cleaned_data.get('photo')

        if photo:
            # Verifica tamanho (máximo 5MB)
            if photo.size > 5 * 1024 * 1024:
                raise ValidationError('A foto deve ter no máximo 5MB.')

            # Verifica tipo
            if not photo.content_type.startswith('image/'):
                raise ValidationError('Arquivo deve ser uma imagem.')

        return photo

    def clean_identity_document(self):
        """Valida documento de identidade"""
        doc = self.cleaned_data.get('identity_document')

        if doc:
            if doc.size > 10 * 1024 * 1024:
                raise ValidationError('O documento deve ter no máximo 10MB.')

            if not doc.name.lower().endswith('.pdf'):
                raise ValidationError('O documento deve estar em formato PDF.')

        return doc

    def clean_proof_of_address(self):
        """Valida comprovante de residência"""
        doc = self.cleaned_data.get('proof_of_address')

        if doc:
            if doc.size > 10 * 1024 * 1024:
                raise ValidationError('O comprovante deve ter no máximo 10MB.')

            if not doc.name.lower().endswith('.pdf'):
                raise ValidationError('O comprovante deve estar em formato PDF.')

        return doc

    def save(self, commit=True):
        """Salva o autor e configura status inicial"""
        author = super().save(commit=False)

        # Configurações iniciais
        author.status = 'pending'
        author.is_active = False
        author.accepted_terms = True

        # Converte lista de gêneros para JSON
        if self.cleaned_data.get('writing_genres'):
            author.writing_genres = list(self.cleaned_data['writing_genres'])

        if commit:
            author.save()

        return author


class AuthorBookForm(forms.ModelForm):
    """Formulário para criar/editar livros de autores."""

    class Meta:
        model = AuthorBook
        fields = [
            'title', 'synopsis', 'genre', 'cover_image',
            'tags', 'status'
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
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'romance, fantasia, aventura (separados por vírgula)'
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
            'tags': 'Tags',
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
