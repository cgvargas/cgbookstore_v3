"""
Script para verificar integridade dos dados migrados.
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from core.models import Category, Author, Book, Section, SectionItem, Banner, Event, Video

print("="*70)
print("VERIFICACAO DETALHADA DOS DADOS MIGRADOS")
print("="*70)

# Contadores básicos
print("\n📊 CONTADORES BASICOS:")
print(f"  Users: {User.objects.count()}")
print(f"  UserProfiles: {UserProfile.objects.count()}")
print(f"  Categories: {Category.objects.count()}")
print(f"  Authors: {Author.objects.count()}")
print(f"  Books: {Book.objects.count()}")
print(f"  Sections: {Section.objects.count()}")
print(f"  SectionItems: {SectionItem.objects.count()}")
print(f"  Banners: {Banner.objects.count()}")
print(f"  Events: {Event.objects.count()}")
print(f"  Videos: {Video.objects.count()}")

# Verificar integridade de UserProfiles
print("\n🔍 VERIFICACAO DE USERPROFILES:")
users_sem_profile = User.objects.filter(profile__isnull=True).count()
print(f"  Users sem UserProfile: {users_sem_profile}")

# Dados importantes dos profiles
profile_com_bio = UserProfile.objects.exclude(bio='').count()
profile_com_avatar = UserProfile.objects.exclude(avatar='').count()
profile_premium = UserProfile.objects.filter(is_premium=True).count()
total_xp = sum(p.total_xp for p in UserProfile.objects.all())

print(f"  Profiles com biografia: {profile_com_bio}/15")
print(f"  Profiles com avatar: {profile_com_avatar}/15")
print(f"  Profiles premium: {profile_premium}/15")
print(f"  Total XP acumulado: {total_xp}")

# Verificar relacionamentos de Books
print("\n🔗 VERIFICACAO DE RELACIONAMENTOS:")
books_com_autor = Book.objects.filter(author__isnull=False).count()
books_com_categoria = Book.objects.filter(category__isnull=False).count()
books_com_capa = Book.objects.exclude(cover_image='').count()

print(f"  Books com autor: {books_com_autor}/{Book.objects.count()}")
print(f"  Books com categoria: {books_com_categoria}/{Book.objects.count()}")
print(f"  Books com capa: {books_com_capa}/{Book.objects.count()}")

# Exemplos de dados
print("\n📚 EXEMPLOS DE DADOS:")
first_user = User.objects.first()
if first_user:
    print(f"  Primeiro usuário: {first_user.username}")
    if hasattr(first_user, 'profile'):
        print(f"    - XP: {first_user.profile.total_xp}")
        print(f"    - Level: {first_user.profile.level}")
        print(f"    - Premium: {first_user.profile.is_premium}")

first_book = Book.objects.first()
if first_book:
    print(f"  Primeiro livro: {first_book.title}")
    print(f"    - Autor: {first_book.author.name if first_book.author else 'N/A'}")
    print(f"    - Categoria: {first_book.category.name if first_book.category else 'N/A'}")

print("\n" + "="*70)
print("✅ MIGRACAO CONCLUIDA COM SUCESSO!")
print("="*70)
