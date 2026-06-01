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
