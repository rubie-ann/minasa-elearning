# Generated migration file for FileAccessLog model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sections', '0016_quizattempt_minigameattempt'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileAccessLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_type', models.CharField(choices=[('view', 'View'), ('download', 'Download')], max_length=10)),
                ('accessed_at', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access_logs', to='sections.section')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='file_access_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'File Access Log',
                'verbose_name_plural': 'File Access Logs',
                'ordering': ['-accessed_at'],
            },
        ),
        migrations.AddIndex(
            model_name='fileaccesslog',
            index=models.Index(fields=['section', '-accessed_at'], name='sections_fi_section_8b7a9c_idx'),
        ),
        migrations.AddIndex(
            model_name='fileaccesslog',
            index=models.Index(fields=['user', '-accessed_at'], name='sections_fi_user_id_9f8b2d_idx'),
        ),
    ]
