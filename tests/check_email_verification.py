"""
Script to check email verification status of users
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from allauth.account.models import EmailAddress
from django.contrib.auth.models import User

print("=" * 60)
print("CHECKING EMAIL VERIFICATION STATUS")
print("=" * 60)

total_users = User.objects.count()
total_emails = EmailAddress.objects.count()

print(f"\nTotal Users: {total_users}")
print(f"Total EmailAddress records: {total_emails}")

verified_count = EmailAddress.objects.filter(verified=True).count()
unverified_count = EmailAddress.objects.filter(verified=False).count()

print(f"\nVerified emails: {verified_count}")
print(f"Unverified emails: {unverified_count}")

if unverified_count > 0:
    print("\n" + "=" * 60)
    print("UNVERIFIED EMAIL ADDRESSES:")
    print("=" * 60)
    for ea in EmailAddress.objects.filter(verified=False):
        print(f"  - {ea.email} (user: {ea.user.username}, primary: {ea.primary})")

# Check users without EmailAddress records
users_without_email = []
for user in User.objects.all():
    if not EmailAddress.objects.filter(user=user).exists():
        users_without_email.append(user)

if users_without_email:
    print("\n" + "=" * 60)
    print("USERS WITHOUT EmailAddress RECORDS:")
    print("=" * 60)
    for user in users_without_email:
        print(f"  - {user.username} ({user.email})")

print("\n" + "=" * 60)
print("CHECKING SPECIFIC USER: claudio.g.vargas@outlook.com")
print("=" * 60)
try:
    email_obj = EmailAddress.objects.get(email='claudio.g.vargas@outlook.com')
    print(f"User: {email_obj.user.username}")
    print(f"Email: {email_obj.email}")
    print(f"Verified: {email_obj.verified}")
    print(f"Primary: {email_obj.primary}")
except EmailAddress.DoesNotExist:
    print("EmailAddress record not found!")
    try:
        user = User.objects.get(email='claudio.g.vargas@outlook.com')
        print(f"User exists: {user.username}")
        print("But NO EmailAddress record!")
    except User.DoesNotExist:
        print("User not found either!")

print("\n" + "=" * 60)
