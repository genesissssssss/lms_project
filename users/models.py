from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Custom User model with role-based access"""
    
    class Role(models.TextChoices):
        STUDENT = 'student', _('Student')
        INSTRUCTOR = 'instructor', _('Instructor')
        ADMIN = 'admin', _('Admin')
    
    # Additional fields
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        help_text="User role in the system"
    )
    bio = models.TextField(blank=True, null=True, help_text="User biography")
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Learning-specific fields
    enrolled_courses_count = models.IntegerField(default=0)
    completed_lessons_count = models.IntegerField(default=0)
    total_learning_time = models.IntegerField(default=0)  # in minutes
    last_active = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_student(self):
        return self.role == self.Role.STUDENT
    
    @property
    def is_instructor(self):
        return self.role == self.Role.INSTRUCTOR
    
    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_superuser