# CLAUDE.md - AI Assistant Guide for CG Bookstore v3

> **Purpose:** This document provides AI assistants with comprehensive context about the CG Bookstore codebase, development workflows, and key conventions to follow when assisting with code modifications, debugging, and feature development.

**Last Updated:** November 22, 2025
**Project Version:** 3.0
**Django Version:** 5.1.1
**Python Version:** 3.11+

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture & Code Structure](#architecture--code-structure)
4. [Development Workflows](#development-workflows)
5. [Key Conventions](#key-conventions)
6. [Database Schema](#database-schema)
7. [API Endpoints](#api-endpoints)
8. [Testing Practices](#testing-practices)
9. [Common Tasks](#common-tasks)
10. [Deployment](#deployment)
11. [Important Gotchas](#important-gotchas)
12. [Troubleshooting](#troubleshooting)

---

## Project Overview

CG Bookstore v3 is a complete virtual bookstore system with AI-powered recommendations, gamification, literary debates, and advanced integrations.

### Core Features

- **AI Recommendations:** Hybrid algorithm (collaborative + content-based + trending) using Google Gemini AI
- **Book Catalog:** Google Books API integration with advanced search and filtering
- **Literary Chatbot:** NLP-powered chat for personalized book recommendations
- **Gamification:** Points, badges, reading challenges, and rankings
- **Financial Module:** Mercado Pago integration for payments and credits
- **Literary Debates:** Forums and moderated discussions by book
- **Social Authentication:** Google and Facebook OAuth via django-allauth
- **Admin Tools:** Web-based tools for Render Free tier (no shell access)

### Production Environment

- **Live URL:** https://cgbookstore-v3.onrender.com
- **Platform:** Render.com (Free tier)
- **Database:** PostgreSQL (Supabase with Transaction Pooler for IPv4)
- **Cache:** Redis (Render-managed)
- **Storage:** Supabase Storage for media files

---

## Technology Stack

### Backend

```python
# Core Framework
Django==5.1.1                    # Main web framework
django-environ==0.12.0           # Environment variables
python-decouple==3.8             # Configuration management

# Authentication
django-allauth==65.13.0          # Social auth (Google, Facebook)
PyJWT==2.10.1                    # JWT tokens

# Database
psycopg[binary]==3.2.12          # PostgreSQL adapter
dj-database-url==3.0.1           # Database URL parsing

# Supabase Integration
supabase==2.23.2                 # Supabase client
storage3==2.23.2                 # File storage

# Cache & Background Tasks
redis==5.2.0                     # Redis client
django-redis==6.0.0              # Django Redis cache backend
celery==5.5.3                    # Background task queue
django-celery-beat==2.8.1        # Periodic tasks

# AI & Machine Learning
google-generativeai==0.8.5       # Google Gemini AI
scikit-learn==1.7.2              # ML algorithms
pandas==2.2.3                    # Data analysis
numpy==2.2.2                     # Numerical computing

# Image Processing
Pillow==11.1.0                   # Image manipulation
django-stdimage==6.0.2           # Standard image fields
opencv-python==4.11.0.86         # Computer vision

# API & REST
djangorestframework==3.16.1      # REST API framework

# Payments
mercadopago==2.3.0               # Mercado Pago integration

# Email
sendgrid==6.11.0                 # SendGrid API
sib-api-v3-sdk==7.6.0            # Brevo (formerly Sendinblue) API

# Text Processing
nltk==3.9.1                      # Natural Language Toolkit
textblob==0.18.0.post0           # Text analysis
beautifulsoup4==4.12.3           # HTML parsing

# Production Server
gunicorn==23.0.0                 # WSGI HTTP Server
whitenoise==6.7.0                # Static file serving
```

### Frontend

- **HTML/CSS:** Bootstrap 4 (via django-bootstrap4)
- **JavaScript:** Vanilla JS with jQuery
- **Templates:** Django Template Language
- **Static Files:** WhiteNoise compression in production

---

## Architecture & Code Structure

### Directory Organization

```
cgbookstore_v3/
├── 📂 Django Apps (Business Logic)
│   ├── accounts/              # User authentication & profiles
│   ├── cgbookstore/           # Project settings & configuration
│   ├── chatbot_literario/     # AI chatbot for book recommendations
│   ├── core/                  # Main app (books, categories, events)
│   │   ├── management/commands/  # Custom Django commands
│   │   ├── models/            # Modular model structure
│   │   ├── views/             # Feature-based view organization
│   │   ├── admin/             # Django admin customizations
│   │   ├── signals/           # Django signals
│   │   └── utils/             # Helper functions
│   ├── debates/               # Literary discussion forums
│   ├── finance/               # Mercado Pago payment integration
│   └── recommendations/       # AI recommendation engine
│
├── 📂 config/                 # Configuration files
│   ├── .env.example           # Environment variable template
│   └── requirements.txt       # Python dependencies (main)
│
├── 📂 deploy/                 # Deployment configuration
│   ├── render.yaml            # Render.com service config
│   └── scripts/build.sh       # Build script for Render
│
├── 📂 docs/                   # Documentation (organized)
│   ├── deployment/            # Deploy guides
│   ├── production/            # Production operation guides
│   ├── setup/                 # Initial setup guides
│   ├── troubleshooting/       # Problem-solving guides
│   └── INDEX.md               # Documentation index
│
├── 📂 templates/              # Django templates
│   ├── account/               # Allauth templates (customized)
│   ├── admin_tools/           # Web-based admin tools
│   ├── core/                  # Core app templates
│   ├── chatbot_literario/     # Chatbot UI
│   ├── debates/               # Debate forum templates
│   ├── finance/               # Payment pages
│   ├── gamification/          # Gamification UI
│   └── recommendations/       # Recommendation UI
│
├── 📂 static/                 # Static files (CSS, JS, images)
├── 📂 media/                  # User uploads (local fallback)
├── 📂 staticfiles/            # Collected static files (production)
│
├── 📂 testes/                 # Test scripts
├── 📂 scripts/                # Utility scripts
│
├── manage.py                  # Django CLI
├── requirements.txt           # Dependencies (symlink to config/)
├── build.sh                   # Build script (symlink to deploy/)
└── render.yaml                # Render config (symlink to deploy/)
```

### App Responsibilities

#### `core/` - Main Application

**Models (Modular Structure):**
- `Book` - Book catalog with Google Books API integration
- `Category` - Book categories and genres
- `Author` - Author information
- `Video` - Educational/promotional videos
- `Section` - Dynamic homepage sections
- `SectionItem` - Items within sections (polymorphic)
- `Event` - Literary events and webinars
- `Banner` - Promotional banners

**Views (Feature-Based Organization):**
- `home_view.py` - Homepage with dynamic sections
- `book_views.py` - Book listing and filtering
- `book_detail_view.py` - Individual book pages
- `book_search_views.py` - Advanced search functionality
- `google_books_views.py` - Google Books API integration
- `library_view.py` - User's personal library
- `library_ajax_views.py` - AJAX endpoints for library
- `gamification_views.py` - Gamification features
- `gamification_api_views.py` - Gamification API endpoints
- `dashboard_view.py` - User dashboard
- `admin_tools.py` - Web-based admin utilities
- `contact_view.py` - Contact form
- `about_view.py` - About page
- `author_views.py` - Author pages
- `event_views.py` - Event management
- `banner_views.py` - Banner display

**Management Commands:**
- `setup_initial_data.py` - Initialize database with categories, books, OAuth apps
- `health_check.py` - System health diagnostics
- `populate_db.py` - Bulk data population
- `migrate_media_to_supabase.py` - Migrate local media to Supabase
- `fix_duplicates.py` - Fix duplicate database entries
- `cleanup_socialapps.py` - Clean up OAuth app duplicates

**Admin Tools (Web-Based - for Render Free):**
- `/admin-tools/health/` - Health check dashboard
- `/admin-tools/setup/` - One-click data initialization

#### `accounts/` - Authentication & Profiles

- User profile management
- Custom django-allauth adapters
- Social authentication integration
- Profile customization

#### `chatbot_literario/` - AI Chatbot

- Conversational book recommendations
- Chat history persistence
- Integration with recommendation engine
- NLP-based query processing

#### `recommendations/` - AI Recommendation Engine

**Key Components:**
- Collaborative filtering (user-based)
- Content-based filtering (book attributes)
- Trending algorithm (popularity + recency)
- Hybrid weighting system
- Redis caching for performance
- Google Gemini AI integration

**Configuration (settings.py):**
```python
RECOMMENDATIONS_CONFIG = {
    'MIN_INTERACTIONS': 5,        # Min interactions for personalized recs
    'CACHE_TIMEOUT': 21600,       # 6 hours cache
    'SIMILARITY_CACHE_TIMEOUT': 86400,  # 24 hours
    'MAX_RECOMMENDATIONS': 10,    # Max results returned
    'HYBRID_WEIGHTS': {
        'collaborative': 0.6,     # 60% collaborative filtering
        'content': 0.3,           # 30% content-based
        'trending': 0.1,          # 10% trending books
    },
}
```

#### `debates/` - Literary Discussions

- Book-specific discussion threads
- Comment moderation
- User engagement tracking

#### `finance/` - Payment Processing

- Mercado Pago integration
- Credit system
- Transaction history
- Payment webhooks

---

## Development Workflows

### Local Development Setup

```bash
# 1. Clone and setup environment
git clone <repo-url>
cd cgbookstore_v3
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp config/.env.example .env
# Edit .env with your credentials

# 4. Initialize database
python manage.py migrate
python manage.py setup_initial_data
python manage.py createsuperuser

# 5. Run development server
python manage.py runserver
```

### Standard Development Cycle

```
1. 💻 Development
   - Make code changes
   - Test locally with runserver

2. 🧪 Testing
   - python manage.py check
   - Manual testing in browser
   - Check console for errors

3. ✅ Pre-commit Checks
   - Verify migrations: python manage.py makemigrations --check
   - Update requirements if needed: pip freeze > config/requirements.txt
   - Test static collection: python manage.py collectstatic --dry-run

4. 📝 Git Commit
   - git add .
   - git commit -m "Type: Clear description"
   - Types: Feature, Fix, Improvement, Docs, Refactor

5. 🚀 Deploy
   - git push origin main
   - Render auto-deploys on push
   - Monitor logs in Render dashboard

6. 🔍 Verify Production
   - Check /admin-tools/health/
   - Test new functionality
   - Review Render logs
```

### Migration Workflow

```bash
# 1. Create migrations
python manage.py makemigrations

# 2. Review migration files
# Check in app_name/migrations/

# 3. Test migration locally
python manage.py migrate

# 4. Verify with showmigrations
python manage.py showmigrations

# 5. Commit migration files
git add */migrations/*.py
git commit -m "Migration: Description of schema change"

# 6. Push to production
git push origin main
# Render runs migrations automatically in build.sh
```

---

## Key Conventions

### Code Style

**Python:**
- Follow PEP 8 style guide
- Use descriptive variable names in Portuguese or English (consistent per file)
- Maximum line length: 120 characters
- Use docstrings for complex functions/classes

**Django Patterns:**
- Fat models, thin views (business logic in models)
- Use Django ORM (avoid raw SQL unless necessary)
- Always use `select_related()` and `prefetch_related()` for foreign keys
- Use Django's built-in validators
- Leverage Django signals for decoupled logic

**Model Organization:**
```python
# Modular approach in core/models/
# Each model in separate file: book.py, category.py, etc.
# All imported in __init__.py

from .category import Category
from .book import Book
# etc.
```

**View Organization:**
```python
# Feature-based organization in core/views/
# Separate files by feature: book_views.py, gamification_views.py
# All imported in __init__.py

from .home_view import home_view
from .book_views import book_list, book_detail
# etc.
```

### Naming Conventions

**Files:**
- Models: `singular_noun.py` (e.g., `book.py`, `author.py`)
- Views: `feature_views.py` (e.g., `book_views.py`, `gamification_views.py`)
- Templates: `feature/action.html` (e.g., `core/book_list.html`)
- URLs: `app_name/urls.py` with namespace

**Database:**
- Table names: Auto-generated by Django (`app_model`)
- Foreign keys: `related_model_id` (Django auto-adds `_id`)
- Many-to-many: Use descriptive `through` model names

**Functions/Methods:**
- Views: `snake_case` (e.g., `book_detail_view`)
- Models: `snake_case` methods, PascalCase class names
- Management commands: `snake_case` (e.g., `setup_initial_data`)

### Environment Variables

**Required (Production):**
```env
SECRET_KEY=<django-secret-key>
DEBUG=False
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
ALLOWED_HOSTS=cgbookstore-v3.onrender.com
CSRF_TRUSTED_ORIGINS=https://cgbookstore-v3.onrender.com
```

**Render Free IPv4 Fix (Supabase):**
```env
# Use Transaction Pooler (recommended)
DATABASE_URL=postgresql://postgres.xxxxx:password@aws-0-us-east-1.pooler.supabase.com:5432/postgres

# OR set manual IPv4 if using direct connection
DATABASE_IPV4=44.XXX.XXX.XXX  # Get via nslookup
```

**Optional APIs:**
```env
GOOGLE_BOOKS_API_KEY=...
GEMINI_API_KEY=...
MERCADOPAGO_ACCESS_TOKEN=...
```

**OAuth (Google/Facebook):**
```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
FACEBOOK_APP_ID=...
FACEBOOK_APP_SECRET=...
```

**Email:**
```env
USE_BREVO_API=true
EMAIL_HOST_PASSWORD=<brevo-api-key>
```

**Supabase Storage:**
```env
USE_SUPABASE_STORAGE=true
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_KEY=...
```

### URL Patterns

```python
# Project-level URLs (cgbookstore/urls.py)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-tools/', include('core.urls_admin_tools', namespace='admin_tools')),
    path('accounts/', include('allauth.urls')),  # BEFORE custom accounts
    path('profile/', include('accounts.urls', namespace='accounts')),
    path('chatbot/', include('chatbot_literario.urls', namespace='chatbot')),
    path('debates/', include('debates.urls')),
    path('recommendations/', include('recommendations.urls', namespace='recommendations')),
    path('finance/', include('finance.urls', namespace='finance')),
    path('', include('core.urls', namespace='core')),  # Last
]

# App-level URLs - always use namespace
# core/urls.py
app_name = 'core'
urlpatterns = [
    path('', home_view, name='home'),
    path('books/', book_list, name='book_list'),
    path('books/<int:pk>/', book_detail, name='book_detail'),
]
```

### Template Conventions

**Structure:**
```
templates/
├── base.html                    # Base template (all pages extend)
├── app_name/
│   ├── feature_list.html        # List views
│   ├── feature_detail.html      # Detail views
│   └── feature_form.html        # Form views
```

**Template Tags:**
```django
{% load static %}                # Static files
{% load custom_filters %}        # Custom template tags
{% url 'app:view_name' %}        # URL reversing with namespace
{% static 'path/file.ext' %}     # Static file reference
```

### Cache Strategy

**Redis Caching (django-redis):**
```python
from django.core.cache import cache

# Cache recommendations (6 hours)
cache_key = f'recommendations_{user.id}'
recommendations = cache.get(cache_key)
if not recommendations:
    recommendations = generate_recommendations(user)
    cache.set(cache_key, recommendations, timeout=21600)

# Cache patterns
# - User-specific: 'prefix_{user.id}'
# - Global: 'prefix_all'
# - Versioned: 'prefix_v1_{id}'
```

**Cache Invalidation:**
- Explicit: `cache.delete(key)` or `cache.delete_pattern('prefix_*')`
- TTL-based: Set appropriate timeout values
- Signal-based: Use Django signals to invalidate on model changes

---

## Database Schema

### Core Models

**Book:**
```python
# core/models/book.py
- title: CharField(max_length=255)
- authors: ManyToManyField(Author)
- category: ForeignKey(Category)
- description: TextField
- cover: ImageField (Supabase Storage or local)
- isbn: CharField(unique=True)
- publisher: CharField
- published_date: DateField
- page_count: IntegerField
- language: CharField
- google_books_id: CharField(unique=True)
- average_rating: DecimalField
- ratings_count: IntegerField
- created_at: DateTimeField(auto_now_add=True)
```

**Category:**
```python
# core/models/category.py
- name: CharField(max_length=100, unique=True)
- description: TextField
- icon: CharField  # FontAwesome icon class
```

**Author:**
```python
# core/models/author.py
- name: CharField(max_length=255)
- bio: TextField
- photo: ImageField
```

**Section (Dynamic Homepage):**
```python
# core/models/section.py
- title: CharField
- description: TextField
- section_type: CharField(choices=SECTION_TYPES)
  # Types: 'featured', 'category', 'author', 'mixed'
- display_order: IntegerField
- is_active: BooleanField
- container_opacity: DecimalField(default=0.0)  # For styling
```

**SectionItem (Polymorphic):**
```python
# core/models/section_item.py
- section: ForeignKey(Section)
- content_type: ForeignKey(ContentType)  # Polymorphic
- object_id: PositiveIntegerField
- content_object: GenericForeignKey()  # Book, Video, etc.
- display_order: IntegerField
```

### User-Related Models

**User Interactions (Gamification):**
- `ReadingProgress` - Track user's reading progress
- `UserBadge` - Achievements earned
- `ReadingChallenge` - Reading challenges
- `UserPoints` - Point accumulation

**Library:**
- `UserLibrary` - Books saved by users
- `BookReview` - User reviews and ratings

### Recommendation Models

```python
# recommendations/models.py
- UserInteraction: User behavior tracking
- BookSimilarity: Precomputed book similarities
- RecommendationCache: Cached recommendations
```

### Finance Models

```python
# finance/models.py
- Transaction: Payment transactions
- UserCredit: User credit balance
- PaymentMethod: Saved payment methods
```

---

## API Endpoints

### REST API (Django REST Framework)

**Authentication:**
- Session-based (Django sessions)
- Basic auth for testing
- Permissions controlled per view

**Recommendations API:**
```
GET /recommendations/api/get/              # Get personalized recommendations
GET /recommendations/api/similar/<book_id>/  # Similar books
GET /recommendations/api/trending/         # Trending books
```

**Gamification API:**
```
GET  /api/gamification/stats/              # User gamification stats
POST /api/gamification/log-action/         # Log user action
GET  /api/gamification/badges/             # User badges
GET  /api/gamification/challenges/         # Active challenges
```

**Library AJAX:**
```
POST /library/add/<book_id>/               # Add book to library
POST /library/remove/<book_id>/            # Remove from library
GET  /library/status/<book_id>/            # Check if in library
```

**Google Books Integration:**
```
GET /books/search/google/                  # Search Google Books
POST /books/import/<google_books_id>/      # Import from Google Books
```

---

## Testing Practices

### Manual Testing

**Primary Method:** Manual browser testing (no automated test suite yet)

**Testing Checklist:**
```bash
# 1. System check
python manage.py check

# 2. Migration verification
python manage.py makemigrations --check --dry-run
python manage.py showmigrations

# 3. Run server
python manage.py runserver

# 4. Manual tests:
- Login/logout flow
- Book search and filtering
- Recommendations display
- Add/remove from library
- Payment flow (test mode)
- Admin tools access
- Social auth (if configured)
```

### Test Scripts

Located in `testes/` directory:
```bash
python testes/test_ai_recommendations.py   # Test recommendation engine
python testes/test_performance.py          # Performance benchmarks
python testes/test_db.py                   # Database connectivity
python testes/test_cache_quick.py          # Redis cache test
```

### Health Check

**Web Interface:**
```
GET /admin-tools/health/
```

**Command Line:**
```bash
python manage.py health_check
```

**Checks:**
- Database connectivity
- Redis connection
- Site configuration (django-allauth)
- OAuth apps setup
- Data counts (books, categories, users)

---

## Common Tasks

### Adding a New Book Model Field

```bash
# 1. Edit model
# core/models/book.py
class Book(models.Model):
    # ... existing fields ...
    new_field = models.CharField(max_length=100, blank=True)

# 2. Create migration
python manage.py makemigrations core

# 3. Review migration file
cat core/migrations/00XX_add_new_field.py

# 4. Test locally
python manage.py migrate

# 5. Update admin (if needed)
# core/admin/book_admin.py
list_display = [..., 'new_field']

# 6. Commit and deploy
git add core/models/book.py core/migrations/00XX_*.py
git commit -m "Feature: Add new_field to Book model"
git push origin main
```

### Adding a New View

```python
# 1. Create view file
# core/views/my_feature_views.py
from django.shortcuts import render
from core.models import Book

def my_feature_view(request):
    """Display my feature."""
    books = Book.objects.all()[:10]
    return render(request, 'core/my_feature.html', {
        'books': books,
    })

# 2. Register in __init__.py
# core/views/__init__.py
from .my_feature_views import my_feature_view

# 3. Add URL
# core/urls.py
path('my-feature/', my_feature_view, name='my_feature'),

# 4. Create template
# templates/core/my_feature.html
{% extends 'base.html' %}
{% block content %}
  <!-- content -->
{% endblock %}
```

### Updating Dependencies

```bash
# 1. Install new package
pip install package-name==version

# 2. Update requirements
pip freeze > config/requirements.txt

# 3. Copy to root (Render compatibility)
cp config/requirements.txt .

# 4. Test locally
python manage.py check

# 5. Commit both files
git add config/requirements.txt requirements.txt
git commit -m "Update: Add package-name==version"
git push origin main
```

### Creating Management Command

```python
# 1. Create command file
# core/management/commands/my_command.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Description of what this command does'

    def add_arguments(self, parser):
        parser.add_argument('--option', type=str, help='Optional argument')

    def handle(self, *args, **options):
        self.stdout.write('Executing command...')
        # Command logic here
        self.stdout.write(self.style.SUCCESS('Command completed!'))

# 2. Run command
python manage.py my_command --option=value
```

### Debugging Production Issues (Render Free)

```bash
# No shell access on Render Free! Use these alternatives:

# 1. Check health status
https://cgbookstore-v3.onrender.com/admin-tools/health/

# 2. View logs
# Render Dashboard > Logs (real-time)

# 3. Run setup tool
https://cgbookstore-v3.onrender.com/admin-tools/setup/
# (Must be logged in as superuser)

# 4. Force redeploy
# Render Dashboard > Manual Deploy > Clear build cache & deploy
```

---

## Deployment

### Render.com Configuration

**Service Type:** Web Service
**Environment:** Python 3
**Build Command:** `./build.sh`
**Start Command:** `gunicorn cgbookstore.wsgi:application`

**Auto-Deploy:** Yes (on push to main branch)

### Build Process (`deploy/scripts/build.sh`)

```bash
# 1. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 2. Collect static files
python manage.py collectstatic --no-input

# 3. Create migrations
python manage.py makemigrations --no-input

# 4. Run migrations
python manage.py migrate --no-input --verbosity 2

# 5. Setup initial data
python manage.py setup_initial_data --skip-superuser

# 6. Fix duplicates
python manage.py fix_duplicates

# 7. Create superuser (if CREATE_SUPERUSER=true)
# Uses SUPERUSER_USERNAME, SUPERUSER_EMAIL, SUPERUSER_PASSWORD
```

### Environment Variables (Render)

**Essential:**
- `SECRET_KEY` - Django secret key
- `DEBUG` - `False` for production
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `ALLOWED_HOSTS` - Your domain
- `CSRF_TRUSTED_ORIGINS` - `https://your-domain.com`

**Optional Superuser Creation:**
- `CREATE_SUPERUSER` - `true` to auto-create
- `SUPERUSER_USERNAME` - Admin username
- `SUPERUSER_EMAIL` - Admin email
- `SUPERUSER_PASSWORD` - Admin password (change after first login!)

### Static Files

**Development:**
- Files served from `static/` directories
- Django's `runserver` serves automatically

**Production:**
- WhiteNoise serves static files
- Compressed and fingerprinted via `CompressedManifestStaticFilesStorage`
- `collectstatic` runs during build

### Media Files

**Local Fallback:**
- Stored in `media/` directory
- Not recommended for production (ephemeral filesystem)

**Supabase Storage (Recommended):**
```python
# settings.py
USE_SUPABASE_STORAGE = True
SUPABASE_URL = 'https://xxxxx.supabase.co'
SUPABASE_ANON_KEY = '...'
SUPABASE_SERVICE_KEY = '...'

# Custom storage backend
# core/storage_backends.py
class SupabaseMediaStorage(Storage):
    # Implementation handles uploads to Supabase
```

### Database Configuration

**Render Free + Supabase Issue:**
- Render Free only supports IPv4
- Supabase direct connection uses IPv6

**Solution 1 (Recommended): Use Supabase Transaction Pooler**
```env
DATABASE_URL=postgresql://postgres.xxxxx:password@aws-0-us-east-1.pooler.supabase.com:5432/postgres
# Pooler provides IPv4 connectivity
```

**Solution 2: Manual IPv4 Configuration**
```env
# Get IPv4 address: nslookup db.xxxxx.supabase.co
DATABASE_IPV4=44.XXX.XXX.XXX
# Settings.py will use this for direct connection
```

### Deployment Checklist

**Before Deploy:**
- [ ] Code tested locally (`python manage.py check`)
- [ ] Migrations created and tested (`makemigrations`, `migrate`)
- [ ] `requirements.txt` updated (if dependencies changed)
- [ ] No credentials in code (use environment variables)
- [ ] Static files collect successfully (`collectstatic --dry-run`)
- [ ] Clear commit message

**After Deploy:**
- [ ] Render build completed without errors
- [ ] Health check passes (`/admin-tools/health/`)
- [ ] Site loads without 500 errors
- [ ] New functionality works as expected
- [ ] Check Render logs for warnings/errors
- [ ] Admin panel accessible

---

## Important Gotchas

### Django-allauth Configuration

**Site Object Required:**
```python
# Django's sites framework SITE_ID must match database
SITE_ID = 1

# Run this to ensure Site exists:
python manage.py setup_initial_data
# OR manually:
from django.contrib.sites.models import Site
Site.objects.get_or_create(id=1, defaults={
    'domain': 'cgbookstore-v3.onrender.com',
    'name': 'CG Bookstore'
})
```

**OAuth Apps Configuration:**
- Credentials stored in database (not settings.py)
- Use Django admin: `/admin/socialaccount/socialapp/`
- OR use `setup_initial_data` command
- Apps must be linked to Site (many-to-many)

**Login Methods:**
```python
# settings.py
ACCOUNT_LOGIN_METHODS = {'email', 'username'}  # Both allowed
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # Send email but don't block login
ACCOUNT_UNIQUE_EMAIL = True  # Prevent duplicate emails
```

### Model Organization

**Modular Models (core/models/):**
```python
# Each model in separate file
# Import all in __init__.py
from .book import Book
from .category import Category
# etc.

__all__ = ['Book', 'Category', ...]
```

**When importing:**
```python
# Correct:
from core.models import Book, Category

# Also correct:
from core.models.book import Book
```

### Cache Considerations

**Redis Fallback:**
```python
# settings.py
CACHES = {
    'default': {
        'OPTIONS': {
            'IGNORE_EXCEPTIONS': True,  # Fallback if Redis fails
        }
    }
}
```

**Cache Invalidation:**
- Always invalidate cache when data changes
- Use signals for automatic invalidation:
```python
from django.db.models.signals import post_save
from django.core.cache import cache

@receiver(post_save, sender=Book)
def invalidate_book_cache(sender, instance, **kwargs):
    cache.delete(f'book_{instance.id}')
    cache.delete_pattern('recommendations_*')
```

### Static Files in Production

**CRITICAL: Run collectstatic**
```bash
# This happens automatically in build.sh
python manage.py collectstatic --no-input
```

**WhiteNoise serves from `staticfiles/` NOT `static/`**

**Template static files:**
```django
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<!-- NOT: /static/css/style.css -->
```

### Migrations on Render Free

**No Shell Access = No Manual Migrations**

**Solution: Migrations run automatically in build.sh**
```bash
python manage.py makemigrations --no-input
python manage.py migrate --no-input
```

**If migrations fail:**
- Check Render build logs
- Verify migration files are committed to git
- May need to create idempotent migrations:
```python
# Use RunPython with checks for existing data
def forwards(apps, schema_editor):
    Model = apps.get_model('app', 'Model')
    if not Model.objects.filter(name='test').exists():
        Model.objects.create(name='test')
```

### URL Namespacing

**Always use namespaces:**
```python
# app/urls.py
app_name = 'myapp'

# In templates:
{% url 'myapp:view_name' %}

# In views:
from django.urls import reverse
reverse('myapp:view_name', kwargs={'pk': 1})
```

**Common mistake:**
```django
<!-- Wrong: -->
{% url 'view_name' %}

<!-- Correct: -->
{% url 'core:view_name' %}
```

### Google Books API Quota

**Free tier limits:**
- 1000 requests/day
- 100 requests/100 seconds

**Best practices:**
- Cache API responses
- Batch requests when possible
- Store imported books in database

### Recommendations Performance

**Heavy computation:**
- Collaborative filtering is CPU-intensive
- Use aggressive caching (6-24 hours)
- Consider background tasks (Celery) for updates

**Cache strategy:**
```python
# Per-user cache (6 hours)
cache_key = f'recommendations_{user.id}'
timeout = 21600

# Similarity cache (24 hours)
cache_key = f'similarity_{book.id}'
timeout = 86400
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: Site returns 500 error after deploy

**Diagnosis:**
```bash
# Check Render logs for traceback
# Common causes:
# - Missing environment variable
# - Database connection failed
# - Static files not collected
# - Migration failed
```

**Solution:**
```bash
# 1. Check /admin-tools/health/
# 2. Review Render logs for specific error
# 3. Verify environment variables in Render dashboard
# 4. Try manual redeploy: Clear build cache & deploy
```

#### Issue: Static files not loading (CSS/JS missing)

**Diagnosis:**
```bash
# Check browser console for 404 errors
# Verify staticfiles/ directory exists
```

**Solution:**
```bash
# Ensure build.sh runs collectstatic
python manage.py collectstatic --no-input

# Verify STATIC_ROOT and STATIC_URL in settings.py
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Check WhiteNoise is in MIDDLEWARE
'whitenoise.middleware.WhiteNoiseMiddleware',
```

#### Issue: OAuth login fails

**Diagnosis:**
```bash
# Error: "SocialApp matching query does not exist"
# OR: "Site matching query does not exist"
```

**Solution:**
```bash
# 1. Verify Site exists
python manage.py setup_initial_data

# 2. Check OAuth apps in admin
# /admin/socialaccount/socialapp/
# - Google and Facebook apps should exist
# - Linked to Site (id=1)
# - Client ID and Secret configured

# 3. Verify redirect URIs match
# Google: https://your-domain.com/accounts/google/login/callback/
# Facebook: https://your-domain.com/accounts/facebook/login/callback/
```

#### Issue: Database connection fails on Render Free

**Diagnosis:**
```bash
# Error: "could not translate host name to address: Name or service not known"
# OR: IPv6 connection errors
```

**Solution:**
```bash
# Use Supabase Transaction Pooler
DATABASE_URL=postgresql://postgres.xxxxx:password@aws-0-us-east-1.pooler.supabase.com:5432/postgres

# OR configure manual IPv4
DATABASE_IPV4=44.XXX.XXX.XXX  # Get via nslookup
```

#### Issue: Redis connection fails

**Diagnosis:**
```bash
# Logs show Redis connection errors
# Features work but slowly (cache disabled)
```

**Solution:**
```bash
# 1. Verify REDIS_URL in environment variables
# 2. Check Redis service is running (Render dashboard)
# 3. Verify IGNORE_EXCEPTIONS is True (allows fallback)

# Settings should have:
CACHES = {
    'default': {
        'OPTIONS': {
            'IGNORE_EXCEPTIONS': True,  # Graceful degradation
        }
    }
}
```

#### Issue: Migrations conflict

**Diagnosis:**
```bash
# Error: "Conflicting migrations detected"
# Multiple migration files for same change
```

**Solution:**
```bash
# Local environment:
# 1. Delete conflicting migration files
# 2. Reset migrations for app
python manage.py migrate app_name zero
python manage.py makemigrations app_name
python manage.py migrate app_name

# 3. Commit corrected migrations
git add app_name/migrations/
git commit -m "Fix: Resolve migration conflicts"
git push

# Production:
# Clear build cache and redeploy
```

#### Issue: Superuser doesn't exist

**Diagnosis:**
```bash
# Can't login to /admin/
# No superuser created
```

**Solution:**
```bash
# Option 1: Use environment variables (Render)
CREATE_SUPERUSER=true
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_PASSWORD=yourpassword
# Then redeploy

# Option 2: Use setup tool
# Login with any admin account, then:
# /admin-tools/setup/
# This creates default superuser if none exists
```

### Performance Optimization

**Database Queries:**
```python
# Always use select_related for ForeignKey
books = Book.objects.select_related('category', 'author').all()

# Use prefetch_related for ManyToMany
books = Book.objects.prefetch_related('authors', 'tags').all()

# Avoid N+1 queries
# Bad:
for book in books:
    print(book.category.name)  # Query per book!

# Good:
for book in books.select_related('category'):
    print(book.category.name)  # Single JOIN query
```

**Caching:**
```python
# Cache expensive operations
from django.core.cache import cache

def get_recommendations(user):
    cache_key = f'recommendations_{user.id}'
    recommendations = cache.get(cache_key)
    if not recommendations:
        recommendations = expensive_recommendation_calculation(user)
        cache.set(cache_key, recommendations, timeout=21600)
    return recommendations
```

**Template Optimization:**
```django
{# Cache template fragments #}
{% load cache %}
{% cache 3600 sidebar request.user.id %}
  <!-- expensive sidebar content -->
{% endcache %}
```

### Debugging Tools

**Health Check Dashboard:**
```
/admin-tools/health/
```
Shows:
- Database status
- Redis status
- Site configuration
- OAuth apps
- Data counts

**Django Debug Toolbar (local only):**
```python
# Enabled when DEBUG=True
# Shows:
# - SQL queries
# - Cache hits/misses
# - Template rendering time
# - Request/response headers
```

**Logging:**
```python
# Use Django logging
import logging
logger = logging.getLogger(__name__)

logger.info('Informational message')
logger.warning('Warning message')
logger.error('Error message')

# Check logs:
# Local: Terminal output
# Render: Dashboard > Logs
```

---

## Additional Resources

### Documentation Files

**Deployment:**
- `docs/deployment/DEPLOY_RENDER.md` - Complete Render deployment guide
- `docs/deployment/PRODUCTION_CHECKLIST.md` - Pre-deploy checklist
- `docs/production/GUIA_RAPIDO_FREE.md` - Render Free tier guide

**Setup:**
- `docs/setup/CONFIGURAR_LOGIN_SOCIAL.md` - OAuth configuration
- `GUIA_CONFIGURACAO_LOCAL.md` - Local development setup

**Troubleshooting:**
- `docs/troubleshooting/TROUBLESHOOTING_PRODUCAO.md` - Production issues
- `docs/production/CORRECOES_PRODUCAO.md` - Quick fixes

**Development:**
- `docs/WORKFLOW_DESENVOLVIMENTO.md` - Development workflow
- `ESTRUTURA_PROJETO.md` - Project structure

### Key Files to Review

**Settings:**
- `cgbookstore/settings.py` - All Django configuration

**URLs:**
- `cgbookstore/urls.py` - Main URL routing
- `core/urls.py` - Core app URLs
- `core/urls_admin_tools.py` - Admin tools URLs

**Models:**
- `core/models/` - All core models
- `recommendations/models.py` - Recommendation models
- `finance/models.py` - Payment models

**Views:**
- `core/views/` - All feature views
- `core/views/admin_tools.py` - Health check & setup tools

**Management Commands:**
- `core/management/commands/setup_initial_data.py` - Database initialization
- `core/management/commands/health_check.py` - System diagnostics

### External Documentation

- **Django 5.1:** https://docs.djangoproject.com/en/5.1/
- **Django-allauth:** https://docs.allauth.org/en/latest/
- **DRF:** https://www.django-rest-framework.org/
- **Render:** https://render.com/docs
- **Supabase:** https://supabase.com/docs
- **Google Books API:** https://developers.google.com/books
- **Mercado Pago:** https://www.mercadopago.com.br/developers

---

## Quick Reference Commands

```bash
# Development
python manage.py runserver              # Start dev server
python manage.py shell                  # Django shell
python manage.py check                  # System check

# Database
python manage.py makemigrations         # Create migrations
python manage.py migrate                # Apply migrations
python manage.py showmigrations         # Show migration status
python manage.py dbshell                # Database shell

# Data Management
python manage.py setup_initial_data     # Initialize database
python manage.py health_check           # System diagnostics
python manage.py populate_db            # Bulk data import
python manage.py createsuperuser        # Create admin user

# Static Files
python manage.py collectstatic          # Collect static files
python manage.py collectstatic --dry-run  # Test collection

# Cache
python manage.py clear_cache            # Clear all cache (if command exists)

# Testing
python manage.py test                   # Run tests (if configured)
python testes/test_ai_recommendations.py  # Test recommendation engine

# Git
git status                              # Check status
git add .                               # Stage all changes
git commit -m "Type: Message"           # Commit
git push origin main                    # Deploy to production
git log --oneline -10                   # Recent commits
```

---

## Contact & Support

**Production URL:** https://cgbookstore-v3.onrender.com
**Admin Panel:** https://cgbookstore-v3.onrender.com/admin/
**Health Check:** https://cgbookstore-v3.onrender.com/admin-tools/health/

**For Issues:**
1. Check `/admin-tools/health/` for system status
2. Review Render logs in dashboard
3. Consult `docs/troubleshooting/` documentation
4. Check recent git commits for breaking changes

---

**Document Maintained By:** Development Team
**For AI Assistants:** This document provides comprehensive context for code assistance. Always verify current state of codebase before making recommendations.
