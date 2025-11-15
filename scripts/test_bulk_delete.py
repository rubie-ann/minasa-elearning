import os, sys, django
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'minasaelearning.settings')
django.setup()
from django.contrib.auth import get_user_model
from django.test import Client
from django.conf import settings

settings.ALLOWED_HOSTS = list(getattr(settings, 'ALLOWED_HOSTS', [])) + ['testserver', '127.0.0.1', 'localhost']

User = get_user_model()
# Create admin
admin, _ = User.objects.get_or_create(username='admin')
admin.set_password('dadah06!')
admin.is_superuser = True
admin.is_staff = True
admin.save()

# Create users to delete
ids = []
for i in range(3):
    u, created = User.objects.get_or_create(username=f'testdel{i}')
    u.set_password('pw')
    u.is_active = True
    u.save()
    ids.append(str(u.id))

print('created test user ids:', ids)

c = Client()
logged = c.login(username='admin', password='dadah06!')
print('admin logged in:', logged)

resp = c.post('/adminpage/user-management/', {'action':'delete', 'user_id': ids}, follow=True)
print('status:', resp.status_code)
print('redirect_chain:', resp.redirect_chain)

# Verify deletion
for uid in ids:
    exists = User.objects.filter(id=uid).exists()
    print(uid, 'exists after delete?', exists)
