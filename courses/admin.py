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
    fields = ['title', 'content', 'order', 'is_free_preview', 'duration']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'level', 'price', 'is_published', 'enrolled_count', 'total_module_display']
    list_filter = ['level', 'is_published', 'is_featured', 'created_at']
    search_fields =['title', 'description', 'instruction__username']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['enrolled_count', 'rating', 'review_count', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', 
          { 'fields': ('title', 'slug', 'description', 'short_description', 'thumbnail', 'promo_video') }),
        ('Organization', 
          { 'fields': ('instructor', 'level', 'category', 'tags')}),
        ('Pricing',
          { 'fields': ('price', 'is_free') }),
        ('Status', 
          { 'fields': ('is_published', 'is_featured', 'published_at')} ),
        ('Statistics', 
          { 'fields': ('enrolled_count', 'rating', 'review_count')}),
    )

    inlines = [ModuleInline]
    actions = ['publish_courses', 'unpublish_courses']