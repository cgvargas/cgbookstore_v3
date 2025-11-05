# Análise do Sistema de Autenticação Atual

**Data:** 2025-11-05
**Projeto:** CGBookstore v3
**Objetivo:** Preparar integração com autenticação social (Google, Facebook, GitHub, etc.)

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura Atual](#arquitetura-atual)
3. [Análise de Componentes](#análise-de-componentes)
4. [Pontos Fortes](#pontos-fortes)
5. [Lacunas Identificadas](#lacunas-identificadas)
6. [Dados do UserProfile](#dados-do-userprofile)
7. [Fluxos de Autenticação](#fluxos-de-autenticação)
8. [Recomendações](#recomendações)

---

## Visão Geral

O sistema atualmente usa o **Django Authentication System** padrão com autenticação baseada em sessão. Não há implementação de autenticação social.

### Stack Atual
- **Framework:** Django 5.1.2
- **Autenticação:** Django built-in auth
- **Sessões:** django.contrib.sessions
- **Backend:** ModelBackend (padrão)
- **Armazenamento de Sessão:** Database-backed sessions

### Funcionalidades Disponíveis
✅ Registro de usuários
✅ Login/Logout
✅ Edição de perfil
✅ Criação automática de perfil (via signals)
✅ Upload de avatar e banner (Supabase Storage)
✅ Sistema de gamificação (XP, níveis, badges)
✅ Integração com Premium (Finance module)

### Funcionalidades Ausentes
❌ Reset de senha
❌ Autenticação social (Google, Facebook, etc.)
❌ Verificação de email
❌ Login com email (atualmente apenas username)
❌ Two-Factor Authentication (2FA)

---

## Arquitetura Atual

### Estrutura de Diretórios

```
accounts/
├── models/
│   ├── __init__.py
│   ├── user_profile.py          # UserProfile com 20+ campos
│   ├── reading_notification.py  # Notificações de leitura
│   ├── campaign_notification.py # Notificações de campanhas
│   └── system_notification.py   # Notificações do sistema
├── views.py                     # Views de auth (register, edit_profile)
├── forms.py                     # UserRegisterForm, UserProfileForm
├── urls.py                      # URL patterns para /accounts/
├── signals.py                   # Auto-criação de UserProfile
├── admin.py                     # Admin customizado
└── templates/
    └── accounts/
        ├── login.html           # Template de login (446 linhas)
        ├── register.html        # Template de registro
        └── edit_profile.html    # Template de edição
```

### Fluxo de Dados

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│       Django Middleware             │
│  - SessionMiddleware                │
│  - AuthenticationMiddleware         │
│  - CsrfViewMiddleware               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│        Auth Views                   │
│  - register_view (accounts/views)   │
│  - LoginView (django.contrib.auth)  │
│  - LogoutView (django.contrib.auth) │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         Models                      │
│  - User (django.contrib.auth)       │
│  - UserProfile (accounts/models)    │
└─────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│       Database (PostgreSQL)         │
│  - auth_user                        │
│  - accounts_userprofile             │
└─────────────────────────────────────┘
```

---

## Análise de Componentes

### 1. URLs (`accounts/urls.py`)

**Endpoints disponíveis:**

```python
/accounts/login/              # LoginView (built-in)
/accounts/logout/             # LogoutView (built-in)
/accounts/register/           # Custom register view
/accounts/profile/edit/       # Custom edit profile view
```

**Análise:**
- ✅ URLs bem organizadas
- ✅ Usa views built-in do Django quando possível
- ❌ Falta endpoint para password reset
- ❌ Falta endpoint para email verification

**Código relevante:**

```python
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html'
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(
        next_page='book_list'
    ), name='logout'),

    path('register/', views.register_view, name='register'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
]
```

### 2. Views (`accounts/views.py`)

#### `register_view`
**Localização:** [accounts/views.py:22-79](accounts/views.py#L22-L79)

**Funcionalidades:**
- Validação de formulário de registro
- Criação de User
- Login automático após registro
- Redirecionamento para home

**Código:**

```python
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}!')
            login(request, user)
            return redirect('book_list')
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})
```

**Análise:**
- ✅ Implementação simples e funcional
- ✅ Login automático é boa UX
- ✅ Mensagem de sucesso clara
- ⚠️  Não verifica email
- ⚠️  Senha não tem requisitos de complexidade

#### `edit_profile_view`
**Localização:** [accounts/views.py:82-185](accounts/views.py#L82-L185)

**Funcionalidades:**
- Edição de dados do perfil
- Upload de avatar e banner para Supabase Storage
- Validação de tamanho de arquivo (2MB)
- Remoção de imagens antigas

**Código chave:**

```python
if 'avatar' in request.FILES:
    avatar_file = request.FILES['avatar']
    if avatar_file.size > 2 * 1024 * 1024:
        messages.error(request, 'Avatar deve ter no máximo 2MB.')
        return redirect('edit_profile')

    # Upload para Supabase
    file_path = f"avatars/{user.id}/{avatar_file.name}"
    success = upload_to_supabase(avatar_file, file_path, bucket_name='user-uploads')

    if success:
        # Remover avatar antigo se existir
        if user.userprofile.avatar:
            old_path = user.userprofile.avatar.split('/')[-2:]
            delete_from_supabase('/'.join(old_path), bucket_name='user-uploads')

        user.userprofile.avatar = file_path
```

**Análise:**
- ✅ Validação robusta de uploads
- ✅ Limpeza de arquivos antigos
- ✅ Integração com Supabase Storage
- ✅ Mensagens de erro claras
- ⚠️  Poderia usar formulários do Django para validação

### 3. Forms (`accounts/forms.py`)

#### `UserRegisterForm`
**Localização:** [accounts/forms.py:8-29](accounts/forms.py#L8-L29)

```python
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email já está cadastrado.')
        return email
```

**Análise:**
- ✅ Valida unicidade de email
- ✅ Usa UserCreationForm (validação de senha built-in)
- ✅ Email obrigatório
- ⚠️  Username obrigatório (poderia permitir login apenas com email)

#### `UserProfileForm`
**Localização:** [accounts/forms.py:32-54](accounts/forms.py#L32-L54)

```python
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'location', 'birth_date', 'website',
            'favorite_genres', 'reading_goal', 'privacy_settings'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'favorite_genres': forms.CheckboxSelectMultiple(),
            'privacy_settings': forms.CheckboxSelectMultiple(),
        }
```

**Análise:**
- ✅ Cobre campos principais do perfil
- ✅ Widgets apropriados (textarea, date picker, checkboxes)
- ✅ Fácil de estender
- ℹ️  Não inclui campos de gamificação (são read-only)

### 4. Models

#### User Model (Django Built-in)
Usa o modelo padrão `django.contrib.auth.models.User`

**Campos principais:**
- `username` (unique)
- `email`
- `password` (hashed)
- `first_name`
- `last_name`
- `is_active`
- `is_staff`
- `is_superuser`
- `date_joined`
- `last_login`

#### UserProfile Model
**Localização:** [accounts/models/user_profile.py:1-466](accounts/models/user_profile.py#L1-L466)

**Relacionamento:**
```python
user = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    related_name='userprofile'
)
```

**Categorias de Campos:**

##### 1. Informações Básicas
```python
bio = models.TextField(max_length=500, blank=True)
location = models.CharField(max_length=100, blank=True)
birth_date = models.DateField(null=True, blank=True)
website = models.URLField(blank=True)
avatar = models.CharField(max_length=255, blank=True)  # Supabase URL
banner = models.CharField(max_length=255, blank=True)  # Supabase URL
```

##### 2. Gamificação
```python
# XP e Níveis
experience_points = models.IntegerField(default=0)
level = models.IntegerField(default=1)

# Conquistas
achievements = models.JSONField(default=list, blank=True)
badges = models.JSONField(default=list, blank=True)

# Estatísticas
total_books_read = models.IntegerField(default=0)
total_pages_read = models.IntegerField(default=0)
total_reading_time = models.IntegerField(default=0)  # em minutos
reading_streak = models.IntegerField(default=0)      # dias consecutivos
longest_streak = models.IntegerField(default=0)
```

##### 3. Preferências de Leitura
```python
favorite_genres = models.JSONField(default=list, blank=True)
reading_goal = models.IntegerField(default=12)  # livros por ano
preferred_language = models.CharField(max_length=10, default='pt-br')
```

##### 4. Premium e Finanças
```python
is_premium = models.BooleanField(default=False)
premium_expires_at = models.DateTimeField(null=True, blank=True)
```

##### 5. Privacidade
```python
privacy_settings = models.JSONField(default=dict, blank=True)
# Exemplo: {'show_reading_list': True, 'show_stats': False}
```

##### 6. Metadados
```python
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
last_activity = models.DateTimeField(auto_now=True)
```

**Métodos importantes:**

```python
def add_experience(self, points):
    """Adiciona XP e verifica level up"""
    self.experience_points += points
    self._check_level_up()
    self.save()

def _check_level_up(self):
    """Calcula nível baseado em XP"""
    # 100 XP por nível, aumentando 10% a cada nível
    pass

def add_achievement(self, achievement_id, name, description):
    """Registra nova conquista"""
    pass

def update_reading_stats(self, pages=0, time_minutes=0):
    """Atualiza estatísticas de leitura"""
    pass
```

**Análise:**
- ✅ Modelo extremamente completo
- ✅ Suporta gamificação robusta
- ✅ Integração com sistema Premium
- ✅ Campos JSON para flexibilidade
- ✅ Métodos auxiliares bem implementados
- ⚠️  Campos `is_premium` e `premium_expires_at` duplicam info de `finance.models.CampaignGrant`

### 5. Signals (`accounts/signals.py`)

**Localização:** [accounts/signals.py:1-25](accounts/signals.py#L1-L25)

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from accounts.models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Cria UserProfile automaticamente quando User é criado"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Garante que UserProfile existe ao salvar User"""
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
    else:
        UserProfile.objects.create(user=instance)
```

**Análise:**
- ✅ Garante que todo User tenha UserProfile
- ✅ Evita erros de RelatedObjectDoesNotExist
- ✅ Implementação robusta com fallback
- ℹ️  Signal registrado em `apps.py` via `ready()`

### 6. Templates

#### `login.html`
**Localização:** [templates/accounts/login.html:1-446](templates/accounts/login.html#L1-L446)

**Características:**
- 446 linhas (template complexo e estilizado)
- Design moderno com animações CSS
- Validação de formulário no frontend
- Mensagens de erro inline
- Links para registro e recuperação de senha (TODO)

**Estrutura:**

```html
<div class="login-container">
    <div class="login-card">
        <h2>Bem-vindo de volta!</h2>
        <form method="post" id="loginForm">
            {% csrf_token %}

            <div class="form-group">
                <label for="username">Usuário</label>
                <input type="text" name="username" required>
            </div>

            <div class="form-group">
                <label for="password">Senha</label>
                <input type="password" name="password" required>
            </div>

            <button type="submit">Entrar</button>
        </form>

        <div class="login-links">
            <a href="{% url 'register' %}">Criar conta</a>
            <a href="#">Esqueci minha senha</a> <!-- TODO -->
        </div>
    </div>
</div>
```

**Análise:**
- ✅ Design profissional e responsivo
- ✅ Boa UX com validações
- ✅ CSRF protection
- ❌ Link "Esqueci minha senha" não funcional
- ⚠️  Não há campo para "Lembrar-me"

#### `register.html`
Similar ao login.html, com campos adicionais:
- Username
- Email
- Password
- Password confirmation

#### `edit_profile.html`
Template complexo com:
- Upload de avatar/banner
- Formulário de dados pessoais
- Seleção de gêneros favoritos
- Configurações de privacidade

### 7. Admin (`accounts/admin.py`)

**Localização:** [accounts/admin.py:1-465](accounts/admin.py#L1-L465)

```python
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'level', 'experience_points', 'is_premium',
        'total_books_read', 'reading_streak'
    )
    list_filter = ('is_premium', 'level', 'created_at')
    search_fields = ('user__username', 'user__email', 'bio')
    readonly_fields = (
        'created_at', 'updated_at', 'last_activity',
        'experience_points', 'level', 'total_books_read'
    )

    fieldsets = (
        ('Usuário', {
            'fields': ('user',)
        }),
        ('Informações Básicas', {
            'fields': ('bio', 'location', 'birth_date', 'website', 'avatar', 'banner')
        }),
        ('Gamificação', {
            'fields': ('experience_points', 'level', 'achievements', 'badges'),
            'classes': ('collapse',)
        }),
        ('Premium', {
            'fields': ('is_premium', 'premium_expires_at')
        }),
        ('Estatísticas', {
            'fields': (
                'total_books_read', 'total_pages_read', 'total_reading_time',
                'reading_streak', 'longest_streak'
            ),
            'classes': ('collapse',)
        }),
    )
```

**Análise:**
- ✅ Interface admin bem organizada
- ✅ Fieldsets lógicos e colapsáveis
- ✅ Campos readonly apropriados
- ✅ Filtros e busca úteis

### 8. Settings (`cgbookstore/settings.py`)

**Configurações de Autenticação:**

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',          # ← Django auth
    'django.contrib.contenttypes',
    'django.contrib.sessions',      # ← Sessions
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ...
    'accounts',                      # ← Nossa app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',      # ← Sessions
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',                 # ← CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',   # ← Auth
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # ← Apenas backend padrão
]

# Redirecionamentos
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/books/'

# Senha
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Sessão
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 semanas
SESSION_COOKIE_SECURE = False  # TODO: True em produção
SESSION_COOKIE_HTTPONLY = True
```

**Análise:**
- ✅ Validadores de senha configurados
- ✅ Session cookies com HTTPOnly
- ✅ CSRF protection ativado
- ⚠️  SESSION_COOKIE_SECURE = False (inseguro para produção)
- ⚠️  Apenas ModelBackend configurado

---

## Pontos Fortes

### 1. Arquitetura Sólida
- ✅ Separação clara de responsabilidades
- ✅ Models bem estruturados
- ✅ Signals para automação
- ✅ Admin interface completa

### 2. UserProfile Robusto
- ✅ 20+ campos cobrindo múltiplas funcionalidades
- ✅ Sistema de gamificação integrado
- ✅ Flexibilidade com JSONField
- ✅ Métodos auxiliares bem implementados

### 3. Segurança Básica
- ✅ CSRF protection
- ✅ Password hashing (built-in Django)
- ✅ Session-based authentication
- ✅ Validadores de senha ativos

### 4. Integração com Supabase
- ✅ Upload de avatares e banners
- ✅ Limpeza de arquivos antigos
- ✅ Validação de tamanho

### 5. UX Cuidadosa
- ✅ Login automático após registro
- ✅ Mensagens de feedback claras
- ✅ Templates bem desenhados
- ✅ Validações no frontend e backend

---

## Lacunas Identificadas

### 🔴 Críticas (Alta Prioridade)

#### 1. Sem Reset de Senha
**Impacto:** Usuários que esquecem senha não conseguem recuperar conta

**Solução:** Implementar `PasswordResetView`, `PasswordResetConfirmView`, etc.

#### 2. Sem Autenticação Social
**Impacto:** Barreira de entrada para novos usuários; UX inferior

**Solução:** Integrar django-allauth com Google, Facebook, GitHub

#### 3. Sem Verificação de Email
**Impacto:** Emails falsos, spam, contas fake

**Solução:** Sistema de confirmação de email via link

### 🟡 Importantes (Média Prioridade)

#### 4. Login Apenas com Username
**Impacto:** Usuários devem lembrar username, não podem usar email

**Solução:** Permitir login com username OU email

#### 5. SESSION_COOKIE_SECURE = False
**Impacto:** Sessões vulneráveis em produção (sem HTTPS)

**Solução:** `SESSION_COOKIE_SECURE = True` em produção

#### 6. Sem Two-Factor Authentication
**Impacto:** Contas vulneráveis a credential stuffing

**Solução:** Implementar 2FA opcional (TOTP via django-otp)

### 🟢 Desejáveis (Baixa Prioridade)

#### 7. Sem "Remember Me"
**Impacto:** UX levemente inferior

**Solução:** Checkbox "Lembrar-me" que estende SESSION_COOKIE_AGE

#### 8. Duplicação de Dados Premium
**Impacto:** Possível inconsistência entre UserProfile.is_premium e CampaignGrant

**Solução:** Usar apenas CampaignGrant como source of truth

#### 9. Sem Rate Limiting
**Impacto:** Vulnerável a brute force attacks

**Solução:** Implementar django-ratelimit ou django-axes

---

## Dados do UserProfile

### Categorização Completa

| Campo | Tipo | Categoria | Editável | Descrição |
|-------|------|-----------|----------|-----------|
| `user` | FK | Relação | ❌ | Relacionamento com User |
| `bio` | Text | Básico | ✅ | Biografia do usuário |
| `location` | Char | Básico | ✅ | Localização |
| `birth_date` | Date | Básico | ✅ | Data de nascimento |
| `website` | URL | Básico | ✅ | Site pessoal |
| `avatar` | Char | Básico | ✅ | URL do avatar (Supabase) |
| `banner` | Char | Básico | ✅ | URL do banner (Supabase) |
| `experience_points` | Int | Gamificação | ❌ | XP acumulado |
| `level` | Int | Gamificação | ❌ | Nível atual |
| `achievements` | JSON | Gamificação | ❌ | Lista de conquistas |
| `badges` | JSON | Gamificação | ❌ | Lista de badges |
| `total_books_read` | Int | Estatísticas | ❌ | Total de livros lidos |
| `total_pages_read` | Int | Estatísticas | ❌ | Total de páginas lidas |
| `total_reading_time` | Int | Estatísticas | ❌ | Tempo total (minutos) |
| `reading_streak` | Int | Estatísticas | ❌ | Sequência atual (dias) |
| `longest_streak` | Int | Estatísticas | ❌ | Maior sequência |
| `favorite_genres` | JSON | Preferências | ✅ | Gêneros favoritos |
| `reading_goal` | Int | Preferências | ✅ | Meta anual |
| `preferred_language` | Char | Preferências | ✅ | Idioma preferido |
| `is_premium` | Bool | Premium | ⚠️ | Status Premium (duplicado?) |
| `premium_expires_at` | DateTime | Premium | ⚠️ | Expiração (duplicado?) |
| `privacy_settings` | JSON | Privacidade | ✅ | Configurações de privacidade |
| `created_at` | DateTime | Metadados | ❌ | Data de criação |
| `updated_at` | DateTime | Metadados | ❌ | Última atualização |
| `last_activity` | DateTime | Metadados | ❌ | Última atividade |

**Total: 24 campos**

### Campos com Potencial Conflito

Os campos `is_premium` e `premium_expires_at` no UserProfile podem conflitar com `finance.models.CampaignGrant`:

```python
# UserProfile
is_premium = models.BooleanField(default=False)
premium_expires_at = models.DateTimeField(null=True, blank=True)

# CampaignGrant
is_active = models.BooleanField(default=True)
expires_at = models.DateTimeField()
```

**Recomendação:** Usar CampaignGrant como source of truth e deprecar campos do UserProfile, ou criar property:

```python
@property
def is_premium(self):
    from finance.models import CampaignGrant
    return CampaignGrant.objects.filter(
        user=self.user,
        is_active=True,
        expires_at__gt=timezone.now()
    ).exists()
```

---

## Fluxos de Autenticação

### Fluxo de Registro

```
┌────────────────┐
│ User acessa    │
│ /register/     │
└────────┬───────┘
         │
         ▼
┌────────────────────────────┐
│ GET /accounts/register/    │
│ → register_view            │
│ → Renderiza formulário     │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ User preenche:             │
│ - username                 │
│ - email                    │
│ - password1                │
│ - password2                │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ POST /accounts/register/   │
│ → register_view            │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ UserRegisterForm           │
│ → Valida dados             │
│ → Verifica email único     │
│ → Valida senha             │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ form.save()                │
│ → Cria User                │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ Signal: post_save          │
│ → Cria UserProfile         │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ login(request, user)       │
│ → Autentica automaticamente│
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ redirect('book_list')      │
│ → User autenticado e       │
│   redirecionado para home  │
└────────────────────────────┘
```

### Fluxo de Login

```
┌────────────────┐
│ User acessa    │
│ /login/        │
└────────┬───────┘
         │
         ▼
┌────────────────────────────┐
│ GET /accounts/login/       │
│ → LoginView (built-in)     │
│ → Renderiza template       │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ User preenche:             │
│ - username                 │
│ - password                 │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ POST /accounts/login/      │
│ → LoginView                │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ AuthenticationForm         │
│ → Valida credenciais       │
│ → Chama authenticate()     │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ ModelBackend               │
│ → Busca user por username  │
│ → Verifica senha (hash)    │
└────────┬───────────────────┘
         │
         ├─────── Credenciais inválidas
         │        └→ Mensagem de erro
         │
         └─────── Credenciais válidas
                  │
                  ▼
         ┌────────────────────────────┐
         │ Cria sessão                │
         │ → session_key salvo em DB  │
         │ → Cookie enviado ao browser│
         └────────┬───────────────────┘
                  │
                  ▼
         ┌────────────────────────────┐
         │ redirect(LOGIN_REDIRECT_URL)│
         │ → Geralmente '/'           │
         └────────────────────────────┘
```

### Fluxo de Edição de Perfil

```
┌────────────────┐
│ User acessa    │
│ /profile/edit/ │
└────────┬───────┘
         │
         ▼
┌────────────────────────────┐
│ @login_required            │
│ → Verifica autenticação    │
└────────┬───────────────────┘
         │
         ├─────── Não autenticado
         │        └→ redirect('/login/')
         │
         └─────── Autenticado
                  │
                  ▼
         ┌────────────────────────────┐
         │ GET /profile/edit/         │
         │ → edit_profile_view        │
         │ → Carrega UserProfileForm  │
         └────────┬───────────────────┘
                  │
                  ▼
         ┌────────────────────────────┐
         │ User edita:                │
         │ - Bio                      │
         │ - Avatar                   │
         │ - Banner                   │
         │ - Gêneros favoritos        │
         │ - Etc.                     │
         └────────┬───────────────────┘
                  │
                  ▼
         ┌────────────────────────────┐
         │ POST /profile/edit/        │
         │ → edit_profile_view        │
         └────────┬───────────────────┘
                  │
                  ▼
         ┌────────────────────────────┐
         │ Valida uploads             │
         │ → Tamanho < 2MB            │
         │ → Formato válido           │
         └────────┬───────────────────┘
                  │
                  ▼
         ┌────────────────────────────┐
         │ Upload para Supabase       │
         │ → avatars/{user_id}/...    │
         │ → banners/{user_id}/...    │
         └────────┬───────────────────┘
                  │
                  ▼
         ┌────────────────────────────┐
         │ Remove arquivos antigos    │
         │ → delete_from_supabase()   │
         └────────┬───────────────────┘
                  │
                  ▼
         ┌────────────────────────────┐
         │ Salva UserProfile          │
         │ → profile.save()           │
         └────────┬───────────────────┘
                  │
                  ▼
         ┌────────────────────────────┐
         │ redirect('edit_profile')   │
         │ → Mensagem de sucesso      │
         └────────────────────────────┘
```

### Fluxo de Verificação de Autenticação (Middleware)

```
┌────────────────┐
│ Request chega  │
└────────┬───────┘
         │
         ▼
┌────────────────────────────┐
│ SessionMiddleware          │
│ → Carrega session do cookie│
│ → session_key → DB lookup  │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ AuthenticationMiddleware   │
│ → Busca user_id na sessão  │
└────────┬───────────────────┘
         │
         ├─────── user_id presente
         │        │
         │        ▼
         │   ┌────────────────────────────┐
         │   │ Carrega User da DB         │
         │   │ → request.user = User      │
         │   └────────────────────────────┘
         │
         └─────── user_id ausente
                  │
                  ▼
         ┌────────────────────────────┐
         │ request.user = AnonymousUser│
         └────────────────────────────┘
                  │
                  ▼
         ┌────────────────────────────┐
         │ View recebe request        │
         │ → Acessa request.user      │
         └────────┬───────────────────┘
                  │
                  ▼
         ┌────────────────────────────┐
         │ @login_required decorator  │
         │ → if not request.user.     │
         │      is_authenticated:     │
         │   redirect(LOGIN_URL)      │
         └────────────────────────────┘
```

---

## Recomendações

### 1. Implementar django-allauth

**Por quê:**
- ✅ Solução madura e bem mantida
- ✅ Suporta 50+ providers (Google, Facebook, GitHub, etc.)
- ✅ Sistema completo de registro, login, email verification
- ✅ Integração fácil com Django existente
- ✅ Mantém auth nativo do Django funcionando

**Providers recomendados (ordem):**
1. **Google** - Mais usado, fácil setup
2. **Facebook** - Popular em BR
3. **GitHub** - Desenvolvedores
4. **Microsoft** - Corporativo
5. **Apple** - iOS users

### 2. Adicionar Password Reset

**Opção A:** Views built-in do Django
```python
# urls.py
path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
```

**Opção B:** django-allauth (incluso)

### 3. Implementar Email Verification

**Com allauth:**
```python
# settings.py
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # ou 'optional'
ACCOUNT_EMAIL_REQUIRED = True
```

### 4. Permitir Login com Email

**Com allauth:**
```python
# settings.py
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'  # ou 'email'
ACCOUNT_USERNAME_REQUIRED = False  # Opcional
```

### 5. Consolidar Dados Premium

**Opção A:** Deprecar campos do UserProfile
```python
# Marcar como deprecated
is_premium = models.BooleanField(
    default=False,
    help_text='DEPRECATED: Use CampaignGrant'
)
```

**Opção B:** Usar properties
```python
@property
def is_premium(self):
    from django.utils import timezone
    from finance.models import CampaignGrant
    return CampaignGrant.objects.filter(
        user=self.user,
        is_active=True,
        expires_at__gt=timezone.now()
    ).exists()

@property
def premium_expires_at(self):
    from finance.models import CampaignGrant
    grant = CampaignGrant.objects.filter(
        user=self.user,
        is_active=True
    ).order_by('-expires_at').first()
    return grant.expires_at if grant else None
```

### 6. Melhorar Segurança em Produção

```python
# settings.py (produção)
SESSION_COOKIE_SECURE = True          # HTTPS only
SESSION_COOKIE_HTTPONLY = True        # Já configurado
SESSION_COOKIE_SAMESITE = 'Lax'       # CSRF protection
CSRF_COOKIE_SECURE = True             # HTTPS only
SECURE_SSL_REDIRECT = True            # Force HTTPS
SECURE_HSTS_SECONDS = 31536000        # HSTS header
```

### 7. Rate Limiting (Opcional)

**Usando django-ratelimit:**
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    # Máximo 5 tentativas por minuto
    pass
```

---

## Próximos Passos

### Fase 1: Fundação (1-2 dias)
1. ✅ Analisar sistema atual (COMPLETO)
2. ⏳ Documentar arquitetura (este documento)
3. ⏳ Criar plano de implementação detalhado
4. ⏳ Definir providers sociais prioritários

### Fase 2: Django-allauth (2-3 dias)
1. Instalar e configurar django-allauth
2. Migrar templates existentes
3. Configurar primeiro provider (Google)
4. Testar fluxos completos
5. Documentar configuração

### Fase 3: Providers Adicionais (1-2 dias)
1. Configurar Facebook
2. Configurar GitHub
3. Configurar Microsoft (opcional)
4. Criar documentação de setup

### Fase 4: Melhorias (1-2 dias)
1. Implementar password reset completo
2. Adicionar email verification
3. Melhorar templates de email
4. Testes end-to-end

### Fase 5: Segurança e Polimento (1 dia)
1. Configurar rate limiting
2. Revisar settings de produção
3. Audit de segurança
4. Documentação final

**Total estimado: 6-10 dias**

---

## Conclusão

O sistema de autenticação atual é **sólido e funcional**, mas possui **lacunas importantes** que impedem uma experiência moderna:

### ✅ Pontos Fortes
- Arquitetura bem estruturada
- UserProfile extremamente completo
- Gamificação integrada
- Segurança básica implementada

### ❌ Lacunas Críticas
- Sem autenticação social
- Sem password reset
- Sem email verification

### 🎯 Solução Recomendada
Integrar **django-allauth** resolve todas as lacunas críticas de forma padronizada e extensível, mantendo 100% de compatibilidade com o sistema existente.

**Próximo passo:** Criar plano detalhado de implementação do django-allauth.

---

**Documento criado em:** 2025-11-05
**Última atualização:** 2025-11-05
**Versão:** 1.0
