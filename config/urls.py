from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# Import views from the correct apps
from users.views import api_home, dashboard, profile, register
from courses import views as course_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Home page
    path('', course_views.course_list, name='home'),
    
    # Course URLs
    path('courses/', course_views.course_list, name='course_list'),
    path('courses/<slug:slug>/', course_views.course_detail, name='course_detail'),
    path('courses/<slug:course_slug>/module/<int:module_order>/lesson/<int:lesson_order>/', 
         course_views.lesson_detail, name='lesson_detail'),
    path('courses/<slug:course_slug>/lesson/<int:lesson_id>/complete/', 
         course_views.mark_lesson_complete, name='mark_lesson_complete'),
    path('courses/<slug:course_slug>/lesson/<int:lesson_id>/quiz/', 
         course_views.save_quiz_result, name='save_quiz_result'),
    
    # User URLs
    path('dashboard/', dashboard, name='dashboard'),
    path('profile/', profile, name='profile'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', register, name='register'),
    
    # API (for future mobile app)
    path('api/', api_home, name='api-home'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)