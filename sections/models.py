from django.db import models

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
    image = models.ImageField(upload_to='section_images/', blank=True, null=True)

    class Meta:
        verbose_name = "Educational Section"
        verbose_name_plural = "Educational Sections"
        
    def __str__(self):
        return f"{self.title} ({self.category})"
