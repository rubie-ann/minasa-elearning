import os
import sys
import django

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'minasaelearning.settings')

django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.conf import settings

# Ensure the test client host is allowed (avoid DisallowedHost during tests)
settings.ALLOWED_HOSTS = list(getattr(settings, 'ALLOWED_HOSTS', [])) + ['testserver', '127.0.0.1', 'localhost']

User = get_user_model()
username = 'admin'
password = 'dadah06!'

# Ensure admin user exists and password set
user, created = User.objects.get_or_create(username=username)
user.set_password(password)
user.is_superuser = True
user.is_staff = True
user.is_active = True
user.save()

client = Client()

urls = ['/', '/users/', '/users/login/', '/users/login']

for url in urls:
    print('\nPOST to', url)
    response = client.post(url, {'username': username, 'password': password}, follow=True)
    print('status:', response.status_code)
    # If redirected, show redirect chain
    if response.redirect_chain:
        print('redirect_chain:', response.redirect_chain)
    # show final path
    try:
        final_url = response.request.get('PATH_INFO')
    except Exception:
        final_url = 'unknown'
    print('final PATH_INFO:', final_url)
    # Print a short snippet of content to see where we landed
    content = response.content.decode('utf-8', errors='ignore')
    snippet = content[:500].replace('\n',' ') if content else ''
    print('content snippet:', snippet)
