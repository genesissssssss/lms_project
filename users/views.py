from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Count, Sum, Avg
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from courses.models import Enrollment, Course, LessonProgress


@api_view(['GET'])
@permission_classes([AllowAny])
def api_home(request):
    """API home endpoint"""
    return Response({
        'message': 'Welcome to LMS API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/token/',
            'users': '/api/users/',
            'courses': '/api/courses/',
        }
    })

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

def register(request):
    """User registration view"""

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Register successfull!')
            return redirect(dashboard)
        else:
            form = UserCreationForm()
        return render(request, 'users/register.html',{'form': form})

