import time
import logging
import sys
from django.contrib.auth import authenticate, login, get_user_model
from django.test import RequestFactory
from importlib import import_module
from django.conf import settings

# Configure logging to output to stdout
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

# Check Redis
from django.core.cache import cache
print("Checking Redis connection...")
try:
    start_redis = time.time()
    cache.set('test_key', 'test_value', 10)
    val = cache.get('test_key')
    print(f"Redis check passed: {val} (Took {time.time() - start_redis:.4f}s)")
except Exception as e:
    print(f"Redis check FAILED: {e}")

User = get_user_model()
username = 'perf_test_user_v2'
password = 'perf_test_password_123'
email = 'perf_test_v2@example.com'

print(f"\n{'='*20} START DEBUG {'='*20}")

try:
    user = User.objects.get(username=username)
    print("User found.")
except User.DoesNotExist:
    user = User.objects.create_user(username=username, email=email, password=password)
    print("User created.")

print("1. Calling authenticate()...")
start = time.time()
user = authenticate(username=username, password=password)
end = time.time()
print(f"AUTHENTICATE took: {end - start:.4f} seconds")

if user:
    factory = RequestFactory()
    request = factory.post('/accounts/login/')
    engine = import_module(settings.SESSION_ENGINE)
    request.session = engine.SessionStore()
    
    print("2. Calling login()...")
    start_login = time.time()
    login(request, user)
    end_login = time.time()
    print(f"LOGIN took: {end_login - start_login:.4f} seconds")
else:
    print("Authentication failed!")

print(f"{'='*20} END DEBUG {'='*20}\n")
