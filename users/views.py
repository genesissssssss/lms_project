from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg
from courses.models import Enrollment, Course, LessonProgress

@login_required
def dashboard(request):
    """Student dashboard showing enrolled courses and progress"""

    #Get all enrollments for the user
    enrollments = Enrollment.ojects.filter(
        student=request.user
    ).select_related('course').prefetch_related(
        'course__module__lessons'
    )

    #Get courses the user is teaching

    teaching_courses = Course.objects.filter(
        instructor=request.user,
        is_published=True
    )

    #calculate statistics
    total_courses = enrollments.count()
    completed_courses = enrollments.filter(status='completed').count()
    in_progress_courses = enrollments.filter(status='active').count()

    # Calculate average progress
    avg_progress = enrollments.aggregate(Avg('process_percentage'))['progress_percentage'] or 0
    
    #Get recent activity
    recent_completions = LessonProgress.objects.filter(
        enrollment__student=request.user,
        is_completed=True
    ).select_related('lesson', 'enrollment__course').order_by('-completed_at')[:5]

    # Get course recommendations
    enrolled_course_ids = enrollments.value_list('course_id', flat=True)
    recommended_courses = Course.objects.filter(
        is_published=True
    ).exclude(
        id__in=enrolled_course_ids
    ).annotate(
        student_count=Count('students')
    ).order_by('-student_count')[:6]
    
    context = {
        'enrollments': enrollments,
        'teaching_courses': teaching_courses,
        'total_courses': total_courses,
        'completed_courses': completed_courses,
        'in_progress_courses': in_progress_courses,
        'avg_progress': round(avg_progress),
        'recent_completions': recent_completions,
        'recommended_courses': recommended_courses,
    }
    
    return render(request, 'users/dashboard.html', context)

@login_required
def profile(request):
    """User profile page"""
    return render(request, 'users/profile.html', {'user': request.user})

