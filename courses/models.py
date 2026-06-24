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
                
        #basic info
        
        module =  models.ForeignKey(
            Module,
            on_delete=models.CASCADE,
            related_name='lessons'
        )
        title = models.Charfield(max_length=200)
        content_type = models.CharField(max_length=20, choices=ContentType.choices)
        order = models.IntegerField(help_text="Order within module")

        #fields
        description = models.TextField(blank=True)
        is_free_preview = models.BooleanField(default=False, help_text="Allow preview without enrollment")

        #video content
        video_url = models.URLField(blank=True, help_text="Youtube/vimeo url or hosted video")
        video_file = models.FileField(upload_to='course_videos/', blank=True, null=True)
        duration = models.IntegerField(blank=True, null=True, help_text="Duration in minutes")

        #For text content
        text_content = models.TextField(blank=True, help_text="HTML or markdown content")

        #for quizess(JSON storage)
        quiz_data = models.JSONField(blank=True, default=dict, help_text="question and answer")
        passing_score = models.IntegerField(default=70, validators=[MinValueValidator(0), MaxValueValidator(100)])

        # for assignments
        assignment_instruction = models.TextField(blank=True)

        #attachments
        attachments = models.FileField(upload_to='lesson_attachments/', blank=True, null=True)

        #statistic
        view_count = models.IntegerField(default=0)
        completed_count = models.IntegerField(default=0)
        created_at = models.DateTimeField(auto_now_add=True)
        uploaded_at = models.DateTimeField(auto_now_add=True)

        class Meta:
            ordering = ['order']
            unique_together = ['module', 'order']

        def __str__(self):
            return f"{self.module.title} - {self.title} "
        
        @property
        def is_video(self):
            return self.content_type == self.ContentType.VIDEO
        @property
        def is_text(self):
            return self.content_type == self.ContentType.TEXT
        
        @property
        def is_quiz(self):
            return self.content_type == self.ContentType.QUIZ
        
        def get_completion_percentage(self):
            """Calculate Completion rate for this grade"""
            if self.view_count == 0:
                return 0
            return (self.completed_count / self.view_count) * 100
        
        class Enrollment(models.Model):
            """Track student enrollment in courses"""

            class Status(models.TextChoices):
                ACTIVE = 'active', 'Active'
                COMPLETED = 'completed', 'Completed'
                DROPPED = 'dropped', 'Dropped'

            student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
            course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')

            status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
            enrolled_at = models.DateTimeField(auto_now_add=True)
            completed_at = models.DateTimeField(blank=True, null=True)

            #progress Tracking
            progress_percentage = models.IntegerField(default=0)
            last_accessed = models.DateTimeField(auto_now=True)

            class Meta:
                unique_together = ['student', 'course']
                ordering = ['-enrolled_at']
            
            def __str__(self):
                return f"{self.student.username} -> {self.course.title}"
            
            def update_progress(self):
              total_lessons = self.course.total_lessons
              if total_lessons == 0:
                  return 0
              completed_lessons = LessonProgress.objects.filter(
                  enrollment=self,
                  is_completed=True
                  ).count()
            
            self.progress_percentage = int((completed_lessons/ total_lesson)* 100)

            if self.progress_percentage == 100 and self.status != self.Status.COMPLETED:
                self.status = self.Status.COMPLETED
                self.completed_at = timezone.now()

                self.save(update_fields=['progress_percentage', 'status', 'completed_at'])
                return self.progress_percentage
            
            class LessonProgress(models.Model):
                """Track individual lesson completion"""

                enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name= "lesson_progress")
                lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress_record")

                is_completed = models.BooleanField(default=False)
                completed_at = models.DateTimeField(blank=True, null= True)
                last_watched_position =  models.IntegerField(default=0, help_text="Video position in seconds")
                time_spent = models.IntegerField(default=0, help_text="Minutes spent on this lesson")

                quiz_score = models.IntegerField(blank=True, null=True)
                quiz_answer = models.JSONField(blank=True, default=dict)

                class Meta:
                    unique_together = ['enrollment', 'lesson']
                
                def __str__(self):
                    status = "✓" if self.is_completed else "O"
                    return f"{status} {self.enrollment.student.username}: {self.lesson.title}"
                
                def complete_lesson(self):
                    """Mark lesson as completed"""

                    if not self.is_completed:
                    self.is_completed = True
                    self.is_completed_at = timezone.now()
                    self.save()

                    #update progress
                    self.enrollment.update_progress()

                def save_quiz_score(self, score, answers):
                    """Save quiz resultt"""
                    self.quiz_score = score
                    self.quiz_answer = answers
                    self.save()
                    #auto complete if pass

                    if score >= self.lesson.passing_score:
                        self.complete_lesson()


