from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from .models import Course, Module, Lesson, Enrollment, LessonProgress
from django.utils import timezone

def course_list(request):
    """Display all published courses with search and filtering"""
    
    # Base queryset - only published courses
    courses = Course.objects.filter(is_published=True)
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # Filter by level
    level = request.GET.get('level', '')
    if level:
        courses = courses.filter(level=level)
    
    # Filter by price (free or paid)
    price = request.GET.get('price', '')
    if price == 'free':
        courses = courses.filter(is_free=True)
    elif price == 'paid':
        courses = courses.filter(is_free=False)
    
    # Sort options
    sort = request.GET.get('sort', '-created_at')
    valid_sorts = ['-created_at', 'created_at', 'title', '-title', 'price', '-price', '-enrolled_count']
    if sort in valid_sorts:
        courses = courses.order_by(sort)
    
    # Annotate with additional data
    courses = courses.annotate(
        module_count=Count('modules'),
        lesson_count=Count('modules__lessons'),
        avg_rating=Avg('rating')
    )
    
    # Check enrollment status for authenticated users
    if request.user.is_authenticated:
        enrolled_course_ids = Enrollment.objects.filter(
            student=request.user
        ).values_list('course_id', flat=True)
    else:
        enrolled_course_ids = []
    
    context = {
        'courses': courses,
        'search_query': search_query,
        'level': level,
        'price': price,
        'sort': sort,
        'enrolled_course_ids': list(enrolled_course_ids),
        'level_choices': Course.Level.choices,
    }
    
    return render(request, 'courses/course_list.html', context)

def course_detail(request, slug):
    """Display course details and modules"""
    
    course = get_object_or_404(
        Course.objects.prefetch_related('modules__lessons'),
        slug=slug,
        is_published=True
    )
    
    # Check if user is enrolled
    is_enrolled = False
    enrollment = None
    if request.user.is_authenticated:
        try:
            enrollment = Enrollment.objects.get(
                student=request.user,
                course=course
            )
            is_enrolled = True
        except Enrollment.DoesNotExist:
            pass
    
    # Check if user is the instructor
    is_instructor = request.user.is_authenticated and request.user == course.instructor
    
    # Get lesson progress for enrolled students
    lesson_progress = {}
    if is_enrolled and enrollment:
        progress_records = LessonProgress.objects.filter(enrollment=enrollment)
        lesson_progress = {record.lesson_id: record for record in progress_records}
    
    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'is_instructor': is_instructor,
        'enrollment': enrollment,
        'lesson_progress': lesson_progress,
    }
    
    return render(request, 'courses/course_detail.html', context)

@login_required
def lesson_detail(request, course_slug, module_order, lesson_order):
    """Display individual lesson content"""
    
    # Get the lesson with all related data
    lesson = get_object_or_404(
        Lesson.objects.select_related('module__course'),
        module__course__slug=course_slug,
        module__order=module_order,
        order=lesson_order,
        module__course__is_published=True
    )
    
    course = lesson.module.course
    
    # Check enrollment or free preview
    is_enrolled = False
    enrollment = None
    
    if request.user.is_authenticated:
        try:
            enrollment = Enrollment.objects.get(
                student=request.user,
                course=course
            )
            is_enrolled = True
        except Enrollment.DoesNotExist:
            pass
    
    # Allow free preview lessons for non-enrolled users
    if not is_enrolled and not lesson.is_free_preview:
        messages.warning(request, 'Please enroll in the course to access this lesson.')
        return redirect('course_detail', slug=course.slug)
    
    # Get or create lesson progress
    lesson_progress = None
    if is_enrolled and enrollment:
        lesson_progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )
    
    # Get all lessons in this module for navigation
    module_lessons = lesson.module.lessons.all().order_by('order')
    
    # Find current index
    current_index = list(module_lessons).index(lesson)
    
    # Get previous and next lessons
    prev_lesson = module_lessons[current_index - 1] if current_index > 0 else None
    next_lesson = module_lessons[current_index + 1] if current_index < len(module_lessons) - 1 else None
    
    # Check if next lesson is locked (for enrolled students only)
    next_locked = False
    if next_lesson and is_enrolled:
        # Check if previous lessons are completed
        previous_lessons = module_lessons[:current_index + 1]
        for prev in previous_lessons:
            try:
                progress = LessonProgress.objects.get(enrollment=enrollment, lesson=prev)
                if not progress.is_completed:
                    next_locked = True
                    break
            except LessonProgress.DoesNotExist:
                next_locked = True
                break
    
    context = {
        'course': course,
        'lesson': lesson,
        'module': lesson.module,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'lesson_progress': lesson_progress,
        'module_lessons': module_lessons,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'next_locked': next_locked,
        'all_modules': course.modules.all().prefetch_related('lessons'),
    }
    
    return render(request, 'courses/lesson_detail.html', context)

@login_required
@require_POST
def mark_lesson_complete(request, course_slug, lesson_id):
    """Mark a lesson as complete"""
    
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course__slug=course_slug)
    
    # Get or create enrollment
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=lesson.module.course
    )
    
    # Get or create lesson progress
    progress, created = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )
    
    # Mark as complete
    progress.complete_lesson()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'progress': enrollment.progress_percentage,
            'completed': progress.is_completed
        })
    
    return redirect('lesson_detail', 
                   course_slug=course_slug,
                   module_order=lesson.module.order,
                   lesson_order=lesson.order)

@login_required
@require_POST
def save_quiz_result(request, course_slug, lesson_id):
    """Save quiz results"""
    
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course__slug=course_slug)
    
    if not lesson.is_quiz:
        return JsonResponse({'error': 'Not a quiz lesson'}, status=400)
    
    # Get the submitted answers
    import json
    data = json.loads(request.body)
    answers = data.get('answers', {})
    
    # Calculate score
    quiz_data = lesson.quiz_data
    questions = quiz_data.get('questions', [])
    
    correct_answers = 0
    total_questions = len(questions)
    
    for idx, question in enumerate(questions):
        if str(idx) in answers and answers[str(idx)] == question.get('correct'):
            correct_answers += 1
    
    score = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
    
    # Save progress
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=lesson.module.course
    )
    
    progress, created = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )
    
    progress.save_quiz_score(score, answers)
    
    return JsonResponse({
        'success': True,
        'score': score,
        'passing': score >= lesson.passing_score,
        'passed': score >= lesson.passing_score,
        'progress': enrollment.progress_percentage
    })