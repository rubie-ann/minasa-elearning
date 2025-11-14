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
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('blocked', 'Blocked'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='images/',
        blank=True,
        null=True,
        default='images/user.png'
    )
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='active',
        help_text="User account status"
    )
    failed_login_attempts = models.IntegerField(
        default=0,
        help_text="Number of consecutive failed login attempts"
    )
    last_failed_login = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="Timestamp of last failed login attempt"
    )
    blocked_until = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="Account blocked until this timestamp"
    )

    def __str__(self):
        return self.user.username
    
    def is_blocked(self):
        """Check if user is currently blocked"""
        from django.utils import timezone
        if self.status == 'blocked':
            return True
        if self.blocked_until and self.blocked_until > timezone.now():
            return True
        return False
    
    def reset_failed_attempts(self):
        """Reset failed login attempts counter"""
        self.failed_login_attempts = 0
        self.last_failed_login = None
        self.blocked_until = None
        self.status = 'active'
        self.save()
    
    def increment_failed_attempts(self):
        """Increment failed login attempts and block if threshold reached"""
        from django.utils import timezone
        from datetime import timedelta
        
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        
        # Block user after 3 failed attempts
        if self.failed_login_attempts >= 3:
            self.status = 'blocked'
            # Block for 30 minutes
            self.blocked_until = timezone.now() + timedelta(minutes=30)
        
        self.save()


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

    
class Category(models.Model):
    """Model for managing content categories"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Quiz(models.Model):
    """Model for quizzes"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Question(models.Model):
    """Model for quiz questions"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Question {self.order}: {self.text[:50]}"


class Answer(models.Model):
    """Model for question answers"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class MinasaProduct(models.Model):
    """Model for Minasa products"""
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    product_name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # ADD THIS LINE

    class Meta:
        verbose_name = "Minasa Product"
        verbose_name_plural = "Minasa Products"
        ordering = ['-id']

    def __str__(self):
        return self.product_name


class MinigameLevel(models.Model):
    """Model for 4 Pics 1 Word minigame levels"""
    image1 = models.ImageField(upload_to='minigame/')
    image2 = models.ImageField(upload_to='minigame/')
    image3 = models.ImageField(upload_to='minigame/')
    image4 = models.ImageField(upload_to='minigame/')
    answer = models.CharField(max_length=50)
    attempts = models.PositiveIntegerField(default=0, help_text="Number of times this level has been attempted")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Minigame Level"
        verbose_name_plural = "Minigame Levels"
        ordering = ['-created_at']

    def __str__(self):
        return f"Level {self.id}: {self.answer}"

    def increment_attempts(self):
        """Increment the attempts counter"""
        self.attempts += 1
        self.save()
    
class GrowthStage(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    image = models.ImageField(upload_to='growth_timeline/', blank=True, null=True)
    order = models.PositiveIntegerField(blank=True, null=True, help_text="Optional manual ordering")

    class Meta:
        ordering = ['date', 'order']

    def __str__(self):
        return f"{self.date} - {self.title}"


class QuizAttempt(models.Model):
    """Model to track user quiz attempts"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-completed_at']
        verbose_name = "Quiz Attempt"
        verbose_name_plural = "Quiz Attempts"

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({self.score}/{self.total_questions})"


class MinigameAttempt(models.Model):
    """Model to track user minigame level attempts"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='minigame_attempts')
    level = models.ForeignKey(MinigameLevel, on_delete=models.CASCADE, related_name='user_attempts')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    attempts_count = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['-completed_at']
        unique_together = ('user', 'level')
        verbose_name = "Minigame Attempt"
        verbose_name_plural = "Minigame Attempts"

    def __str__(self):
        return f"{self.user.username} - Level {self.level.id} {'(Completed)' if self.completed else '(Incomplete)'}"
