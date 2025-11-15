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

# allow testclient host
settings.ALLOWED_HOSTS = list(getattr(settings, 'ALLOWED_HOSTS', [])) + ['testserver', '127.0.0.1', 'localhost']

User = get_user_model()
username = 'admin'
password = 'dadah06!'

# Ensure admin exists
user, created = User.objects.get_or_create(username=username)
user.set_password(password)
user.is_superuser = True
user.is_staff = True
user.is_active = True
user.save()

c = Client()
logged_in = c.login(username=username, password=password)
print('logged_in:', logged_in)
resp = c.get('/adminpage/feedbacks-json/')
print('status:', resp.status_code)
print('content:', resp.content.decode('utf-8')[:1000])
