import os
import sys
import django

# Make sure the project root (where manage.py lives) is importable so
# "minasaelearning.settings" can be imported when running this script.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'minasaelearning.settings')

django.setup()

from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

username = 'admin'
password = 'dadah06!'

user, created = User.objects.get_or_create(username=username)
user.set_password(password)
user.is_superuser = True
user.is_staff = True
user.is_active = True
user.save()

print(f"Admin user created (True means newly created): {created}")

user_auth = authenticate(username=username, password=password)

print('authenticate returned:', user_auth)
if user_auth:
    print('user id:', user_auth.id)
    print('is_superuser:', user_auth.is_superuser)
    # backend may be present if authenticate succeeded
    print('backend attribute present:', hasattr(user_auth, 'backend'))
else:
    print('Authentication failed for admin user')

# Also output where the DB file is (for sanity)
import django.conf
print('DATABASES setting:', django.conf.settings.DATABASES)
print('Using DB file (if sqlite):', django.conf.settings.DATABASES.get('default', {}).get('NAME'))
