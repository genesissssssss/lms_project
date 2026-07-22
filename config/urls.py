"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views import api_home
from courses import views as course_views
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),

    #Home page
    path('', course_views.course_list, name='home'),

    #course urls
    path('courses/', course_views.course_list, name='course_list'),
    path('courses/<slug:slug>/', course_views.course_detail, name='course_detail'),
    path('courses/<slug:course_slug>/module/<int:module_order>/lesson/<int:lesson_order>/', course_views.lesson_detail, name='lesson_detail'),
    path('courses/<slug:course_slug>/lesson/<int:lesson_id>/complete/', course_views.mark_lesson_complete, name='mark_lesson_complete'),
    path('courses/<slug:course_slug>/lesson/<int:lesson_id>/quiz/', course_views.save_quiz_result, name='save_quiz_result'),

    # User URLs
    path('dashboard/', user_views.dashboard, name='dashboard'),
    path('profile/', user_views.profile, name='profile'),
    
    # API (for future mobile app)
    path('api/', api_home, name='api-home'),

]
# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
