# CLAUDE.md - AI Assistant Guide for CG Bookstore v3

> **Last Updated:** 2025-11-20
> **Project Version:** 3.0
> **Django Version:** 5.1.1
> **Python Version:** 3.11+

This document provides comprehensive guidance for AI assistants working with the CG Bookstore v3 codebase. It covers architecture, conventions, workflows, and best practices specific to this project.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Structure](#architecture--structure)
3. [Technology Stack](#technology-stack)
4. [Key Conventions](#key-conventions)
5. [Development Workflows](#development-workflows)
6. [Testing Guidelines](#testing-guidelines)
7. [Deployment Process](#deployment-process)
8. [Common Tasks](#common-tasks)
9. [Important Notes for AI Assistants](#important-notes-for-ai-assistants)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

**CG Bookstore v3** is a feature-rich literary platform for the Brazilian market with:

- **AI-powered recommendation engine** (Google Gemini + hybrid algorithms)
- **Gamification system** (XP, achievements, badges, rankings)
- **Premium subscription service** (R$ 9.90/month via Mercado Pago)
- **Social authentication** (Google, Facebook OAuth)
- **Personal library management** with reading progress tracking
- **Literary debate forums** with voting system
- **E-commerce functionality** (physical books, ebooks)
- **Literary chatbot** for personalized recommendations
- **Video library** (YouTube, Vimeo integration)

**Production URL:** https://cgbookstore-v3.onrender.com

**Target Audience:** Brazilian readers (Portuguese language)

---

## 🏗️ Architecture & Structure

### Django Applications (6 apps)

```
cgbookstore_v3/
├── core/                   # Books, authors, categories, videos, events, sections
├── accounts/              # Authentication, profiles, gamification, notifications
├── recommendations/       # AI recommendation engine (Gemini, scikit-learn)
├── finance/              # Premium subscriptions, e-commerce, Mercado Pago
├── debates/              # Literary forums with voting
├── chatbot_literario/    # AI chatbot for book recommendations
└── cgbookstore/          # Main Django configuration
```

### Key Directories

```
├── templates/            # 47 HTML templates (Django templating)
├── static/
│   ├── css/             # 10 CSS files (themes, library, gamification)
│   ├── js/              # 13 JavaScript files (AJAX, charts, managers)
│   └── images/          # Static images
├── media/               # User uploads (covers, profiles, videos)
├── docs/                # 31+ markdown documentation files
│   ├── deployment/      # Render.com deployment guides
│   ├── production/      # Production operations
│   ├── setup/           # Configuration guides
│   └── troubleshooting/ # Common issues and solutions
├── scripts/
│   ├── setup/           # Local environment setup
│   ├── maintenance/     # Database and cache maintenance
│   └── testing/         # Test automation scripts
├── config/              # Environment and configuration files
└── deploy/              # Deployment scripts and configuration
```

### Database Models Summary

**Core app (8 models):**
- Book, Author, Category, Video, Event, Banner, Section, SectionItem

**Accounts app (14 models):**
- UserProfile, BookShelf, ReadingProgress, BookReview
- BaseNotification, ReadingNotification, SystemNotification, CampaignNotification
- Achievement, UserAchievement, Badge, UserBadge
- MonthlyRanking, XPMultiplier

**Recommendations app (4 models):**
- UserProfile, UserBookInteraction, BookSimilarity, Recommendation

**Finance app (7 models):**
- Subscription, Product, Order, OrderItem, TransactionLog, Campaign, CampaignGrant

**Debates app (3 models):**
- DebateTopic, DebatePost, DebateVote

**Total: ~35 models**

---

## 🔧 Technology Stack

### Core Framework
- **Django 5.1.1** (latest stable)
- **Python 3.11+** (required)
- **ASGI/WSGI** support

### Database & Caching
- **PostgreSQL** (primary database via psycopg[binary] 3.2.12)
- **Redis 5.2.0** (caching with django-redis 6.0.0)
- **Supabase 2.23.2** (cloud storage with local fallback)

### AI & Machine Learning
- **Google Gemini AI** (google-generativeai 0.8.5) - Premium recommendations
- **scikit-learn 1.7.2** - Collaborative filtering
- **numpy 2.2.2**, **pandas 2.2.3**, **scipy 1.16.3** - Data processing
- **NLTK 3.9.1**, **TextBlob 0.18.0** - Natural language processing

### Authentication
- **django-allauth 65.13.0** (social auth)
- **PyJWT 2.10.1** (JSON Web Tokens)
- OAuth providers: Google, Facebook

### Payment Processing
- **mercadopago 2.3.0** (Brazilian payment gateway - PIX, credit card, boleto)

### Background Tasks
- **Celery 5.5.3** (task queue)
- **django-celery-beat 2.8.1** (scheduled tasks)

### Frontend
- **Bootstrap 5.3.0** (responsive framework)
- **Font Awesome 6.4.0** (icons)
- **Swiper 11** (carousels)
- **SweetAlert2** (beautiful alerts)
- **Vanilla JavaScript** (no jQuery)

### Production Server
- **Gunicorn 23.0.0** (WSGI server)
- **WhiteNoise 6.7.0** (static file serving)

### Email
- **Brevo/Sendinblue** (sib-api-v3-sdk 7.6.0) - Primary
- **SendGrid** (sendgrid 6.11.0) - Alternative

---

## 📐 Key Conventions

### Code Style

1. **Python**: Follow PEP 8
   - 4 spaces for indentation
   - Max line length: 120 characters (Django convention)
   - Use descriptive variable names (Portuguese OK for domain terms)

2. **Django Models**:
   - Use `models/` directory for apps with multiple models
   - Import in `models/__init__.py`: `from .book import Book`
   - Abstract base classes: Prefix with `Base` (e.g., `BaseNotification`)
   - Use `related_name` for all ForeignKey relationships
   - Add `verbose_name` and `verbose_name_plural` for admin
   - Add `__str__()` method returning meaningful representation

3. **URL Patterns**:
   - Use `path()` over `re_path()` where possible
   - Name all URL patterns: `name='book_detail'`
   - Organize URLs in `urls.py` per app
   - Use slugs for public-facing URLs: `/livro/nome-do-livro/`

4. **Templates**:
   - Extend from `base.html`
   - Use `{% load static %}` at top of template
   - Block structure: `{% block title %}`, `{% block content %}`
   - Template names match view purpose: `book_list.html`, `book_detail.html`

5. **Static Files**:
   - CSS: Component-based naming (e.g., `library-profile.css`, `gamification.css`)
   - JavaScript: Feature-based naming (e.g., `library-manager.js`, `reading-progress.js`)
   - Use `{% static 'path/to/file' %}` in templates
   - Never hardcode paths

### Language and Localization

- **Primary Language:** Portuguese (pt-br)
- **Timezone:** America/Sao_Paulo
- **Currency:** Brazilian Real (R$)
- **Date Format:** DD/MM/YYYY
- **Code Comments:** Portuguese or English (be consistent per file)
- **User-facing text:** Always Portuguese
- **Technical documentation:** Portuguese preferred, English acceptable

### File Naming

- **Python files:** `snake_case.py`
- **Templates:** `snake_case.html`
- **CSS/JS:** `kebab-case.css`, `kebab-case.js`
- **Documentation:** `SCREAMING_SNAKE_CASE.md` for guides, `lowercase.md` for specific docs

### Git Conventions

- **Branch naming:** `claude/feature-name-sessionid` (auto-generated)
- **Commit messages:**
  - Use conventional commits format
  - Start with verb: "Add", "Fix", "Update", "Remove", "Refactor"
  - Be descriptive: "Fix: Ajustes de UX em cards de livros"
  - Reference issues when applicable: "#123"

### Database Conventions

- **Table names:** Auto-generated by Django (`appname_modelname`)
- **Field naming:** `snake_case`
- **Foreign keys:** End with `_id` (auto-added by Django)
- **Many-to-many:** Plural names (e.g., `categories`, `tags`)
- **Migrations:** Never edit existing migrations, always create new ones

---

## 🔄 Development Workflows

### Local Development Setup

```bash
# 1. Clone and navigate
cd /home/user/cgbookstore_v3

# 2. Activate virtual environment (if not already active)
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 5. Setup database
python manage.py migrate
python manage.py setup_initial_data

# 6. Create superuser
python manage.py createsuperuser

# 7. Run development server
python manage.py runserver
```

### Making Changes

**ALWAYS follow this workflow:**

1. **Understand the codebase first**
   - Read relevant models in `app/models/`
   - Check existing views in `app/views.py` or `app/views/`
   - Review templates in `templates/app/`
   - Check URL patterns in `app/urls.py`

2. **Plan your changes**
   - Use TodoWrite tool to track tasks
   - Break complex changes into steps
   - Identify affected files

3. **Make changes incrementally**
   - Edit models → Create migrations
   - Update views → Update templates
   - Add/modify URLs if needed
   - Update JavaScript/CSS if needed
   - Update tests

4. **Test locally**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver
   # Test in browser
   ```

5. **Commit and push**
   ```bash
   git add .
   git commit -m "Clear description of changes"
   git push -u origin claude/branch-name-sessionid
   ```

### Working with Models

**When adding/modifying models:**

1. Edit model file in `app/models/model_name.py`
2. Update `app/models/__init__.py` if new model
3. Register in `app/admin.py` for Django admin
4. Create migration:
   ```bash
   python manage.py makemigrations app_name
   ```
5. Review migration file in `app/migrations/`
6. Apply migration:
   ```bash
   python manage.py migrate
   ```
7. Update related views, forms, serializers

**Migration Best Practices:**
- Review auto-generated migrations before applying
- Add `default=` or `null=True` when adding non-nullable fields
- Use `RunPython` for data migrations
- Never edit applied migrations
- Test migrations locally before pushing

### Working with Templates

**Template Inheritance:**

```django
{# templates/base.html - Base template #}
<!DOCTYPE html>
<html>
<head>
    {% load static %}
    <title>{% block title %}CG Bookstore{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'css/themes.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% include 'partials/navbar.html' %}
    {% block content %}{% endblock %}
    {% include 'partials/footer.html' %}
    {% block extra_js %}{% endblock %}
</body>
</html>

{# templates/core/book_detail.html - Child template #}
{% extends 'base.html' %}
{% load static %}

{% block title %}{{ book.title }} - CG Bookstore{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/book-detail.css' %}">
{% endblock %}

{% block content %}
<div class="container">
    <h1>{{ book.title }}</h1>
    {# Content here #}
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/book-detail.js' %}"></script>
{% endblock %}
```

### Working with Static Files

**CSS Organization:**
- Theme variables defined in `static/css/themes.css`
- Component styles in separate files
- Use CSS custom properties for consistency
- Responsive: Mobile-first approach

**JavaScript Organization:**
- Feature-based modules (e.g., `library-manager.js`)
- Use vanilla JavaScript (no jQuery)
- AJAX calls to Django views/APIs
- Handle CSRF tokens properly:
  ```javascript
  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  fetch(url, {
      method: 'POST',
      headers: {
          'X-CSRFToken': csrftoken,
          'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
  });
  ```

### Working with Cache

**Redis is used for:**
- Recommendation caching (1 hour TTL)
- Session storage
- Temporary data

**Cache Management:**
```bash
# Clear all caches
python scripts/maintenance/clear_recommendations_cache.py

# Or via Django shell
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

**Cache Keys Convention:**
- `recs:user:{user_id}` - User recommendations
- `book_sim:{book_id}` - Book similarity
- Use descriptive keys with colons as separators

---

## 🧪 Testing Guidelines

### Test File Locations

- Unit tests: `app/tests.py` or `app/tests/`
- Integration tests: `scripts/testing/`
- Test utilities: `scripts/testing/` with descriptive names

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts

# Run specific test file
python manage.py test accounts.tests.TestUserProfile

# Run with coverage (if installed)
coverage run --source='.' manage.py test
coverage report
```

### Writing Tests

**Follow Django TestCase conventions:**

```python
from django.test import TestCase
from django.contrib.auth.models import User
from core.models import Book

class BookModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.book = Book.objects.create(
            title="Test Book",
            slug="test-book",
            description="Test description"
        )

    def test_book_str_representation(self):
        """Test __str__ method"""
        self.assertEqual(str(self.book), "Test Book")

    def test_book_slug_generation(self):
        """Test automatic slug generation"""
        book = Book.objects.create(title="Another Book")
        self.assertEqual(book.slug, "another-book")
```

### Integration Testing Scripts

**Use shell-based tests for rapid iteration:**

```python
# scripts/testing/quick_test_preferences.py
from recommendations.models import UserProfile, Recommendation
from django.contrib.auth.models import User

# Test recommendation generation
user = User.objects.first()
profile = UserProfile.objects.get(user=user)
recommendations = Recommendation.get_recommendations(user)
print(f"Generated {len(recommendations)} recommendations")
```

**Run with:**
```bash
python manage.py shell
exec(open('scripts/testing/quick_test_preferences.py', encoding='utf-8').read())
```

### Testing Best Practices

1. **Always test locally before pushing**
2. **Write tests for new features**
3. **Test edge cases** (empty data, invalid input, missing relations)
4. **Use fixtures** for complex test data
5. **Mock external APIs** (Google Books, Gemini, Mercado Pago)
6. **Test permissions** (authenticated, anonymous, staff)
7. **Test forms and validation**

---

## 🚀 Deployment Process

### Platform: Render.com (Free Tier)

**Services:**
- Web Service (Python 3.11, Gunicorn)
- PostgreSQL Database (free tier)
- Redis (free tier)

**Configuration:** `render.yaml` (auto-deployment)

### Deployment Workflow

1. **Push to branch:**
   ```bash
   git push -u origin claude/branch-name-sessionid
   ```

2. **Render auto-detects changes** (if connected to main branch)
   - Or trigger manual deploy in Render dashboard

3. **Build process** (`build.sh`):
   - Install dependencies
   - Collect static files (WhiteNoise)
   - Run migrations
   - Setup initial data (categories, Site, OAuth apps)
   - Create superuser (if env vars set)

4. **Service starts:**
   ```bash
   gunicorn cgbookstore.wsgi:application --bind 0.0.0.0:$PORT --timeout 180
   ```

### Environment Variables (Render Dashboard)

**Required:**
```
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgresql://... (auto-set by Render)
REDIS_URL=redis://... (auto-set by Render)
ALLOWED_HOSTS=cgbookstore-v3.onrender.com
CSRF_TRUSTED_ORIGINS=https://cgbookstore-v3.onrender.com
```

**Optional (but recommended):**
```
# OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
FACEBOOK_APP_ID=...
FACEBOOK_APP_SECRET=...

# APIs
GOOGLE_BOOKS_API_KEY=...
GEMINI_API_KEY=...

# Storage
USE_SUPABASE_STORAGE=true
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_KEY=...

# Payments
MERCADOPAGO_ACCESS_TOKEN=...
MERCADOPAGO_PUBLIC_KEY=...

# Email
USE_BREVO_API=true
EMAIL_HOST_PASSWORD=your-brevo-api-key

# Auto-create superuser on deploy
CREATE_SUPERUSER=true
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_PASSWORD=secure-password
```

### Post-Deployment Checks

**Use web-based admin tools (no shell access on free tier):**

1. **Health Check:** `https://cgbookstore-v3.onrender.com/admin-tools/health/`
   - Database connection ✓
   - Redis connection ✓
   - Site configuration ✓
   - OAuth apps ✓
   - Data counts ✓

2. **Setup Data:** `https://cgbookstore-v3.onrender.com/admin-tools/setup/`
   - Creates categories
   - Creates sample books
   - Configures Site for django-allauth
   - Sets up OAuth apps

3. **Admin Panel:** `https://cgbookstore-v3.onrender.com/admin/`
   - Verify superuser can login
   - Check data integrity

### Deployment Troubleshooting

**Common issues and solutions:**

| Issue | Solution |
|-------|----------|
| Static files not loading | Check STATIC_ROOT, run collectstatic, verify WhiteNoise |
| Database errors | Verify DATABASE_URL, check migrations applied |
| Redis errors | Verify REDIS_URL, check Redis service running |
| OAuth not working | Check redirect URIs match SITE_URL in Google/Facebook console |
| 502/503 errors | Check logs in Render dashboard, verify Gunicorn timeout |
| Migrations pending | Re-deploy or use Render shell (paid plan) |

**View logs:**
```
Render Dashboard > cgbookstore > Logs
```

### Git Best Practices for Deployment

1. **Always push to feature branch first**
2. **Test in staging (if available)**
3. **Never push directly to main**
4. **Use pull requests for review**
5. **Tag releases:** `git tag v3.0.1`

---

## 📝 Common Tasks

### Task 1: Add a New Book Model Field

```bash
# 1. Edit model
# File: core/models/book.py
# Add field: isbn13 = models.CharField(max_length=13, blank=True)

# 2. Create migration
python manage.py makemigrations core

# 3. Review migration
# File: core/migrations/000X_add_isbn13.py

# 4. Apply migration
python manage.py migrate core

# 5. Update admin (if needed)
# File: core/admin.py
# Add 'isbn13' to list_display or fieldsets

# 6. Update templates (if needed)
# File: templates/core/book_detail.html

# 7. Test locally
python manage.py runserver

# 8. Commit and push
git add .
git commit -m "Add ISBN13 field to Book model"
git push
```

### Task 2: Create a New View

```python
# File: core/views.py or core/views/book_views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Book

@login_required
def book_detail(request, slug):
    """Display book details"""
    book = get_object_or_404(Book, slug=slug)
    context = {
        'book': book,
        'similar_books': book.get_similar_books()[:5],
    }
    return render(request, 'core/book_detail.html', context)
```

```python
# File: core/urls.py

from django.urls import path
from .views import book_detail

app_name = 'core'

urlpatterns = [
    path('livro/<slug:slug>/', book_detail, name='book_detail'),
]
```

```django
{# File: templates/core/book_detail.html #}

{% extends 'base.html' %}

{% block title %}{{ book.title }}{% endblock %}

{% block content %}
<div class="container">
    <h1>{{ book.title }}</h1>
    <p>{{ book.description }}</p>
</div>
{% endblock %}
```

### Task 3: Add Management Command

```python
# File: core/management/commands/sync_google_books.py

from django.core.management.base import BaseCommand
from core.models import Book
import requests

class Command(BaseCommand):
    help = 'Sync book data from Google Books API'

    def add_arguments(self, parser):
        parser.add_argument('--isbn', type=str, help='Specific ISBN to sync')

    def handle(self, *args, **options):
        isbn = options.get('isbn')
        if isbn:
            self.stdout.write(f'Syncing book with ISBN {isbn}...')
            # Sync logic here
        else:
            self.stdout.write('Syncing all books...')
            # Bulk sync logic here

        self.stdout.write(self.style.SUCCESS('Successfully synced books'))
```

**Usage:**
```bash
python manage.py sync_google_books
python manage.py sync_google_books --isbn=9788535908770
```

### Task 4: Clear Cache

```bash
# Option 1: Python script
python scripts/maintenance/clear_recommendations_cache.py

# Option 2: Django shell
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
>>> exit()

# Option 3: Bash script (clears all)
./clear_all_caches.sh

# Option 4: Restart Redis (nuclear option)
# Local: sudo systemctl restart redis
# Render: Restart Redis service in dashboard
```

### Task 5: Create Sample Data

```bash
# Use built-in management command
python manage.py setup_initial_data

# Or web-based (production without shell)
# Visit: /admin-tools/setup/

# Custom data population
python manage.py populate_db

# Specific sections
python manage.py populate_sections
```

### Task 6: Debug Recommendation System

```bash
# Quick diagnostics
./diagnose_recommendations.sh

# Detailed health check
./check_recommendations_health.sh

# Test preferences
python manage.py shell
exec(open('scripts/testing/quick_test_preferences.py', encoding='utf-8').read())

# Test AI recommendations
python scripts/testing/test_ai_recommendations.py
```

### Task 7: Handle Media Files

```bash
# Migrate to Supabase (cloud storage)
python manage.py migrate_media_to_supabase

# Migrate from Supabase to local
python manage.py migrate_from_supabase

# Sync media paths
python manage.py sync_media_paths

# Fix book covers
python manage.py fix_book_covers
python manage.py update_covers_google
```

### Task 8: Manage Campaigns

```bash
# Create campaign for specific user
python scripts/create_campaign_for_user.py

# Process active campaigns (send notifications)
python manage.py process_campaigns

# Check expiring premium subscriptions
python manage.py check_expiring_premium

# Test campaign with notification
python scripts/create_test_campaign_with_notification.py
```

---

## 🤖 Important Notes for AI Assistants

### Understanding the Codebase

1. **Start with exploration**
   - Use Task tool with Explore agent for open-ended searches
   - Read README.md first for project overview
   - Check docs/ directory for specific topics
   - Review model files to understand data structure

2. **Models are in subdirectories**
   - Core models: `core/models/book.py`, `core/models/author.py`, etc.
   - Accounts models: `accounts/models/profile.py`, `accounts/models/gamification.py`, etc.
   - Always import from `app.models`: `from core.models import Book`

3. **Views can be split**
   - Simple apps: `app/views.py`
   - Complex apps: `app/views/feature_views.py`
   - Check both locations

4. **Templates follow app structure**
   - App templates: `templates/app_name/template_name.html`
   - Base template: `templates/base.html`
   - Partials: `templates/partials/navbar.html`

### Code Modification Guidelines

**DO:**
- ✅ Read files before editing them
- ✅ Use Edit tool for existing files
- ✅ Create migrations after model changes
- ✅ Test changes locally (suggest commands)
- ✅ Follow existing code patterns in the file
- ✅ Add docstrings to new functions/classes
- ✅ Update related templates/views/URLs
- ✅ Check for Portuguese strings in user-facing code
- ✅ Use TodoWrite for multi-step tasks
- ✅ Commit with clear, descriptive messages

**DON'T:**
- ❌ Create new files when editing existing ones works
- ❌ Use Write tool on existing files without reading first
- ❌ Skip migration creation after model changes
- ❌ Edit existing migration files
- ❌ Break existing functionality
- ❌ Remove code without understanding its purpose
- ❌ Change API responses without checking JavaScript usage
- ❌ Modify production settings without confirmation
- ❌ Push to main branch directly

### Django-Specific Patterns

1. **URL Reverse Resolution**
   ```python
   # In views
   from django.urls import reverse
   url = reverse('core:book_detail', kwargs={'slug': book.slug})

   # In templates
   {% url 'core:book_detail' slug=book.slug %}
   ```

2. **Query Optimization**
   ```python
   # Use select_related for ForeignKey
   books = Book.objects.select_related('author', 'category').all()

   # Use prefetch_related for ManyToMany
   books = Book.objects.prefetch_related('categories', 'tags').all()
   ```

3. **Django ORM Patterns**
   ```python
   # Get or 404
   book = get_object_or_404(Book, slug=slug)

   # Get or create
   profile, created = UserProfile.objects.get_or_create(user=user)

   # Filter with Q objects
   from django.db.models import Q
   books = Book.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
   ```

4. **Signals Usage**
   ```python
   # In models.py or signals.py
   from django.db.models.signals import post_save
   from django.dispatch import receiver

   @receiver(post_save, sender=User)
   def create_user_profile(sender, instance, created, **kwargs):
       if created:
           UserProfile.objects.create(user=instance)
   ```

### Working with External APIs

1. **Google Books API**
   - API key in `settings.GOOGLE_BOOKS_API_KEY`
   - Used in `core/views/book_views.py` for search
   - Example endpoint: `https://www.googleapis.com/books/v1/volumes?q={query}`

2. **Google Gemini AI**
   - API key in `settings.GEMINI_API_KEY`
   - Used in `recommendations/` for premium users
   - Rate limits apply - cache results

3. **Mercado Pago**
   - Access token in `settings.MERCADOPAGO_ACCESS_TOKEN`
   - Used in `finance/` for payments
   - Webhook URL must be configured in Mercado Pago dashboard
   - Test with sandbox credentials first

4. **Supabase Storage**
   - URL and keys in settings
   - Used for media file storage (optional)
   - Fallback to local storage if disabled

### Performance Considerations

1. **Database Queries**
   - Always use `select_related()` and `prefetch_related()`
   - Avoid N+1 queries in loops
   - Use `only()` and `defer()` for large models
   - Index frequently queried fields

2. **Caching Strategy**
   - Cache expensive computations (recommendations)
   - Set appropriate TTLs (1 hour for recommendations)
   - Clear cache when underlying data changes
   - Use cache versioning for breaking changes

3. **Static Files**
   - Minify CSS/JS in production (future task)
   - Use WhiteNoise for static serving
   - Consider CDN for images (future task)

4. **Background Tasks**
   - Use Celery for long-running operations
   - Process campaigns asynchronously
   - Send bulk emails in batches
   - Generate recommendations in background

### Security Considerations

1. **Authentication**
   - Always use `@login_required` decorator for protected views
   - Check permissions: `if request.user.is_staff:`
   - Validate user owns resource before modifying

2. **CSRF Protection**
   - Include `{% csrf_token %}` in all forms
   - Send CSRF token in AJAX requests (X-CSRFToken header)

3. **Input Validation**
   - Use Django forms for validation
   - Sanitize user input
   - Use `get_object_or_404()` to prevent info leakage

4. **Environment Variables**
   - Never commit `.env` file
   - All secrets in environment variables
   - Use `python-decouple` for config

### Debugging Strategies

1. **Django Debug Toolbar** (local only)
   ```python
   # Add to INSTALLED_APPS if DEBUG=True
   'debug_toolbar',
   ```

2. **Logging**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.debug(f"Processing book: {book.title}")
   logger.error(f"Failed to fetch from API: {error}")
   ```

3. **Django Shell**
   ```bash
   python manage.py shell
   >>> from core.models import Book
   >>> Book.objects.count()
   >>> book = Book.objects.first()
   >>> book.title
   ```

4. **Print Debugging**
   ```python
   print(f"DEBUG: {variable}")  # Quick and dirty
   import pdb; pdb.set_trace()  # Breakpoint
   ```

### Common Pitfalls to Avoid

1. **Migration Issues**
   - Never edit applied migrations
   - Always run `makemigrations` before `migrate`
   - Check for conflicts in migration dependencies
   - Squash migrations if they become too many (100+)

2. **Import Errors**
   - Circular imports: Import inside function if needed
   - Missing `__init__.py`: Ensure all model directories have it
   - Import from correct location: `from app.models import Model`

3. **Template Errors**
   - Missing `{% load static %}`
   - Incorrect context variable names
   - Missing closing tags: `{% endblock %}`
   - Unescaped variables: Use `|safe` only when necessary

4. **Static Files Not Loading**
   - Run `collectstatic` in production
   - Check STATIC_URL and STATIC_ROOT in settings
   - Verify WhiteNoise is in MIDDLEWARE
   - Clear browser cache

5. **Redis Connection Issues**
   - Verify Redis is running: `redis-cli ping`
   - Check REDIS_URL in settings
   - Connection limit on free tier (30 connections)
   - Clear cache if corrupted: `cache.clear()`

---

## 🆘 Troubleshooting

### Problem: Books not showing in catalog

**Checklist:**
1. Check if books exist: `Book.objects.count()`
2. Run setup: `python manage.py setup_initial_data`
3. Check view filters: Are books being filtered out?
4. Check permissions: Are books published?
5. Clear cache: Stale cache might be serving old data

### Problem: Recommendations not working

**Diagnostic steps:**
```bash
# 1. Run diagnostics
./diagnose_recommendations.sh

# 2. Check Redis connection
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value')
>>> cache.get('test')

# 3. Clear recommendations cache
python scripts/maintenance/clear_recommendations_cache.py

# 4. Test algorithm
exec(open('scripts/testing/quick_test_preferences.py', encoding='utf-8').read())

# 5. Check for user interactions
>>> from recommendations.models import UserBookInteraction
>>> UserBookInteraction.objects.filter(user=user).count()
```

### Problem: OAuth login failing

**Checklist:**
1. Verify Site domain in admin: `/admin/sites/site/`
   - Should match production URL exactly
2. Check OAuth credentials in environment variables
3. Verify redirect URIs in Google/Facebook console:
   - Google: `https://your-domain.com/accounts/google/login/callback/`
   - Facebook: `https://your-domain.com/accounts/facebook/login/callback/`
4. Check SocialApp in admin: `/admin/socialaccount/socialapp/`
5. Run cleanup: `python manage.py cleanup_socialapps`

### Problem: Static files not loading in production

**Fix:**
```bash
# 1. Collect static files
python manage.py collectstatic --no-input

# 2. Verify WhiteNoise configuration in settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Must be here
    ...
]

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 3. Check STATIC_URL in templates
{% load static %}
<link rel="stylesheet" href="{% static 'css/styles.css' %}">

# 4. Re-deploy
git push -u origin branch-name
```

### Problem: Database migrations pending

**In production (Render free tier without shell):**
1. Trigger manual deploy in Render dashboard
2. Build script automatically runs migrations
3. Check logs for migration errors
4. If failed, fix locally and re-deploy

**Locally:**
```bash
# Check migration status
python manage.py showmigrations

# Create missing migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# If conflicts, resolve dependencies in migration files
```

### Problem: 500 Internal Server Error

**Debugging steps:**
1. Check logs in Render dashboard
2. Look for traceback in logs
3. Common causes:
   - Missing environment variables
   - Database connection failed
   - Redis connection failed
   - Missing migrations
   - Static files not collected
4. Enable DEBUG=True temporarily (LOCAL ONLY)
5. Check `/admin-tools/health/` for diagnostic info

### Problem: Mercado Pago webhook failing

**Checklist:**
1. Verify webhook URL in Mercado Pago dashboard
   - Should be: `https://your-domain.com/finance/webhook/`
2. Check access token is correct
3. Review TransactionLog model for errors:
   ```python
   from finance.models import TransactionLog
   logs = TransactionLog.objects.order_by('-created_at')[:10]
   for log in logs:
       print(log.status, log.response_data)
   ```
4. Test with Mercado Pago sandbox first

### Problem: Background tasks not running

**Celery configuration:**
```bash
# 1. Check Celery is configured in settings.py
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# 2. Start Celery worker (local)
celery -A cgbookstore worker -l info

# 3. Start Celery beat (scheduled tasks)
celery -A cgbookstore beat -l info

# 4. Check task status
python manage.py shell
>>> from celery.result import AsyncResult
>>> result = AsyncResult('task-id')
>>> result.status
```

**Note:** Render free tier doesn't support background workers. Use management commands with cron jobs instead.

### Getting Help

1. **Documentation:** Check `docs/` directory first
2. **Health Check:** `/admin-tools/health/` for system status
3. **Logs:** Render Dashboard > cgbookstore > Logs
4. **Django Admin:** `/admin/` for data inspection
5. **Shell Access:** Local only (not on Render free tier)

---

## 📚 Additional Resources

### Documentation Files

**Essential Guides:**
- `README.md` - Project overview and quick start
- `ESTRUTURA_PROJETO.md` - Detailed project structure
- `docs/deployment/DEPLOY_RENDER.md` - Complete deployment guide
- `docs/production/GUIA_RAPIDO_FREE.md` - Quick guide for free tier

**Setup Guides:**
- `GUIA_CONFIGURACAO_LOCAL.md` - Local setup instructions
- `docs/setup/CONFIGURAR_LOGIN_SOCIAL.md` - OAuth configuration

**Troubleshooting:**
- `TROUBLESHOOTING_CACHE.md` - Cache-related issues
- `docs/troubleshooting/TROUBLESHOOTING_PRODUCAO.md` - Production issues

**Testing:**
- `GUIA_TESTE_LOCAL.md` - Local testing guide
- `docs/testing/COMO_TESTAR_PRIORIZACAO.md` - Test prioritization

### External Documentation

- **Django 5.1:** https://docs.djangoproject.com/en/5.1/
- **django-allauth:** https://django-allauth.readthedocs.io/
- **Render.com:** https://render.com/docs
- **Google Books API:** https://developers.google.com/books
- **Google Gemini AI:** https://ai.google.dev/docs
- **Mercado Pago:** https://www.mercadopago.com.br/developers
- **Supabase:** https://supabase.com/docs
- **Redis:** https://redis.io/docs/

### Management Commands Reference

Run `python manage.py help` to see all available commands, including:
- `setup_initial_data` - Initialize database with sample data
- `health_check` - Complete system diagnostics
- `populate_db` - Large-scale data population
- `migrate_media_to_supabase` - Cloud storage migration
- `process_campaigns` - Execute marketing campaigns
- `check_expiring_premium` - Premium subscription notifications

---

## 🎯 Quick Reference

### File Locations Cheat Sheet

| What | Where |
|------|-------|
| Models | `app/models/` or `app/models.py` |
| Views | `app/views.py` or `app/views/` |
| URLs | `app/urls.py` |
| Templates | `templates/app/` |
| Static CSS | `static/css/` |
| Static JS | `static/js/` |
| Admin | `app/admin.py` |
| Tests | `app/tests.py` or `app/tests/` |
| Management commands | `app/management/commands/` |
| Settings | `cgbookstore/settings.py` |
| Main URLs | `cgbookstore/urls.py` |
| Documentation | `docs/` |
| Scripts | `scripts/` |

### Command Cheat Sheet

```bash
# Development
python manage.py runserver
python manage.py shell
python manage.py test

# Database
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations

# Setup
python manage.py setup_initial_data
python manage.py createsuperuser
python manage.py collectstatic

# Diagnostics
python manage.py health_check
./diagnose_recommendations.sh
./check_recommendations_health.sh

# Cache
python scripts/maintenance/clear_recommendations_cache.py
./clear_all_caches.sh

# Git
git status
git add .
git commit -m "message"
git push -u origin branch-name
```

### URL Patterns Cheat Sheet

| URL | Purpose |
|-----|---------|
| `/` | Homepage |
| `/admin/` | Django admin panel |
| `/admin-tools/health/` | Health check dashboard |
| `/admin-tools/setup/` | Data population tool |
| `/livros/` | Book catalog |
| `/livro/<slug>/` | Book detail |
| `/perfil/` | User profile |
| `/biblioteca/` | Personal library |
| `/debates/` | Literary forums |
| `/recomendacoes/` | AI recommendations |
| `/accounts/login/` | Login page |
| `/accounts/google/login/` | Google OAuth |
| `/accounts/facebook/login/` | Facebook OAuth |

---

## ✅ Checklist for AI Assistants

Before completing any task, verify:

- [ ] Read relevant files before editing
- [ ] Understand existing code patterns
- [ ] Use TodoWrite for multi-step tasks
- [ ] Created migrations if models changed
- [ ] Updated related views/templates/URLs
- [ ] Maintained Portuguese strings for users
- [ ] Followed PEP 8 and Django conventions
- [ ] Added docstrings to new functions
- [ ] Tested changes locally (or suggested test commands)
- [ ] Committed with clear message
- [ ] Pushed to correct branch (claude/*)
- [ ] No secrets or credentials in code
- [ ] No breaking changes to existing API
- [ ] Documentation updated if needed

---

**Last Updated:** 2025-11-20
**Maintained By:** AI Assistants working with CG Bookstore v3

For questions or clarifications, refer to the extensive documentation in the `docs/` directory or use the health check tool at `/admin-tools/health/`.
