from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Course, Module, Lesson, Enrollment, LessonProgress

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    fields = ['title', 'order', 'estimated_time']

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'content_type', 'order', 'is_free_preview', 'duration']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'level', 'price', 'is_published', 'enrolled_count', 'total_modules_display']
    list_filter = ['level', 'is_published', 'is_featured', 'created_at']
    search_fields = ['title', 'description', 'instructor__username']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['enrolled_count', 'rating', 'review_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'short_description', 'thumbnail', 'promo_video')
        }),
        ('Organization', {
            'fields': ('instructor', 'level', 'category', 'tags')
        }),
        ('Pricing', {
            'fields': ('price', 'is_free')
        }),
        ('Status', {
            'fields': ('is_published', 'is_featured', 'published_at')
        }),
        ('Statistics', {
            'fields': ('enrolled_count', 'rating', 'review_count')
        }),
    )
    
    inlines = [ModuleInline]
    actions = ['publish_courses', 'unpublish_courses']
    
    def total_modules_display(self, obj):
        """Display total number of modules"""
        return obj.modules.count()
    total_modules_display.short_description = 'Modules'
    
    def publish_courses(self, request, queryset):
        """Publish selected courses"""
        updated = queryset.update(is_published=True)
        self.message_user(request, f'{updated} courses published.')
    publish_courses.short_description = 'Publish selected courses'
    
    def unpublish_courses(self, request, queryset):
        """Unpublish selected courses"""
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} courses unpublished.')
    unpublish_courses.short_description = 'Unpublish selected courses'

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course_link', 'order', 'lesson_count']
    list_filter = ['course']
    search_fields = ['title', 'description']
    inlines = [LessonInline]
    
    def course_link(self, obj):
        """Link to the course in admin"""
        url = reverse('admin:courses_course_change', args=[obj.course.id])
        return format_html('<a href="{}">{}</a>', url, obj.course.title)
    course_link.short_description = 'Course'
    
    def lesson_count(self, obj):
        """Count lessons in this module"""
        return obj.lessons.count()
    lesson_count.short_description = 'Lessons'

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module_link', 'content_type', 'order', 'is_free_preview', 'duration']
    list_filter = ['content_type', 'is_free_preview', 'module__course']
    search_fields = ['title', 'description']
    
    def module_link(self, obj):
        """Link to the module in admin"""
        url = reverse('admin:courses_module_change', args=[obj.module.id])
        return format_html('<a href="{}">{}</a>', url, obj.module.title)
    module_link.short_description = 'Module'

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'status', 'progress_percentage', 'enrolled_at']
    list_filter = ['status', 'course']
    search_fields = ['student__username', 'course__title']
    readonly_fields = ['enrolled_at', 'last_accessed']

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'lesson', 'is_completed', 'quiz_score', 'time_spent']
    list_filter = ['is_completed', 'lesson__content_type']
    search_fields = ['enrollment__student__username', 'lesson__title']