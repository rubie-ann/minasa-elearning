from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class Section(models.Model):
    CATEGORY_CHOICES = [
        ("Planting", "Planting"),
        ("Cultural", "Cultural"),
        ("Historical", "Historical"),
        ("Economic", "Economic Value"),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    image = models.ImageField(upload_to='images/', blank=True, null=True)

    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Educational Section"
        verbose_name_plural = "Educational Sections"
        
    def __str__(self):
        return f"{self.title} ({self.category})"
    
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='images/',
        blank=True,
        null=True,
        default='images/user.png'
    )

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class FestivalEvent(models.Model):
    EVENT_TYPES = [
        ('Parade', 'Parade'),
        ('Competition', 'Competition'),
        ('Concert', 'Concert'),
        ('Exhibit', 'Exhibit'),
        ('Trade Fair', 'Trade Fair'),
        ('Religious', 'Religious'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, default='Other')
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    map_link = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='festival_events/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.event_type})"
