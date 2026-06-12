from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinLengthValidator,  MaxLengthValidator

User = get_user_model()

class Course(models.Model):
    """"Main course model"""

    class Level(models.TextChoices):
        BIGINNER = 'beginner', 'Beginner'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        ADVANCE = 'advance', 'Advanace'
        ALL_LEVELS = 'all_levels', 'All Levels'


title = models.CharField(max_length=200, help_text="Course title")
slug = models.SlugField(unique=True, help_text="URL=friendly version of title") 
description = models.TextField(help_text="Detailed course description")
short_description = models.CharField(max_length=300, help_text="Brief summary for listings")

#media
thumbnail = models.ImageField(upload_to='course_thumbanails/', blank=True, null=True)
promo_video = models.URLField(blank=True, help_text="Youtube/Vimeo URL")

#Organization
level = models.CharField(max_length=100, default='Programming')
tags = models.CharField(max_length=200, blank=True, help_text="Comma-seperated tags")

#pricing
price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
is_free = models.BooleanField(default=False)

#relationships

instructor = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name='courses_teaching',
    limit_choices_to={'role__in': ['instructor', 'admin']}
)
students =models.ManyToManyField(
    User,
    related_name='courses_enrolled',
    blank=True,
    through='Enrollment'
)

#statistic

enrolled_count = models.IntegerField(default=0)
rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.000)
review_count = models.IntegerField(default=0)

#status
is_published = models.BooleanField(default=False)
is_featured = models.BooleanField(default=False)

#Timestamps
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
published_at = models.DateTimeField(blank=True, null=True)

class Meta:
    ordering = ['-created_at']
    indexes = [
        models.Index(fields=['slug']),
        models.Index(fields=['level', 'is_published']),
    ]
def __str__(self):
    return self.title

def save (self, *args, **kwargs):
    if self.is_published and not self.published_at:
        self.published_at = timezone.now()
    super().save(*args, **kwargs)

    @property 
    def total_modules(self):
        return self.modules.count()
    @property
    def total_duration_minutes(self):
        """Calculate total course duration from video lessons"""
        total = 0
        for module in self.modules.all():
            for lesson in module.lessons.all():
                if lesson.duration:
                    total += lesson.duration
        return total
    
    class Module(models.Model):
        """Course module/section"""

        course = models.ForeignKey(
            Course,
            on_delete=models.CASCADE,
            related_name='modules'
        )
        title = models.CharField(max_length=200)
        description = models.TextField(blank=True)
        order = models.IntegerField(help_text="Order in which module appears")
        estimated_time = models.IntegerField(blank=True, null=True, help_text="Minutes to Complete")
        
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        class Meta:
            ordering = ['order']
            unique_together = ['course', 'order']

        def __str__(self):
            return f"{self.course.title} - {self.title}"
        
        @property
        def lesson_count(self):
            return self.lesson.count()
        
        class Lesson(models.Model):
            """Indiviual lesson"""

            class ContenType(models.TextChoices0):
                VIDEO = 'video', 'Video Lesson'
                TEXT = 'text', 'Text Lesson'
                QUIZ = 'quiz', 'Quiz'
                ASSIGNMENT = 'assignment', 'Assignment'
