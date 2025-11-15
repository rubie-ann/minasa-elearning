"""
URL configuration for minasaelearning project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from sections import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('sections.urls')),
    path('', views.login_view, name='login'),  # default page is login
    path('adminpage/admin-dashboard/', views.admin_dashboard, name='adminpage-admin-dashboard'),
    path('adminpage/minasa-products/', views.adminpage_minasa_products, name='adminpage-minasa-products'),
    path('adminpage/user-management/', views.user_management, name='adminpage-user-management'),
    path('adminpage/user-performance/', views.user_performance, name='adminpage-user-performance'),
    path('adminpage/content-manager/', views.content_manager, name='adminpage-content-manager'),
    path('adminpage/category-manager/', views.category_manager, name='adminpage-category-manager'),
    path('adminpage/activities/', views.adminpage_activities, name='adminpage-activities'),
    path('adminpage/festival-calendar/', views.adminpage_festival_calendar, name='adminpage-festival-calendar'),
    path('adminpage/minasa-products/', views.adminpage_minasa_products, name='adminpage-minasa-products'),
    path('adminpage/user-action/', views.user_management, name='adminpage-user-action'),  # For POST requests
    path('adminpage/minigame/', views.admin_minigame, name='adminpage-minigame'),
    path('minigame/add-level/', views.add_minigame_level, name='add_minigame_level'),
    path('adminpage/edit-minigame-level/<int:level_id>/', views.edit_minigame_level, name='edit_minigame_level'),
    path('adminpage/delete-minigame-level/<int:level_id>/', views.delete_minigame_level, name='delete_minigame_level'),
    path('adminpage/get-minigame-level-data/<int:level_id>/', views.get_minigame_level_data, name='get_minigame_level_data'),
    path('accounts/profile/', views.profile_view, name='accounts_profile'),
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', views.logout_view, name='logout'),
    path('generate-report/', views.generate_content_report, name='generate_content_report'),
    path('generate-user-report/', views.generate_user_report, name='generate_user_report'),
    # JSON endpoints for admin UI
    path('adminpage/feedbacks-json/', views.admin_feedbacks_json, name='adminpage-feedbacks-json'),
    # API endpoints for saving quiz and minigame attempts
    path('api/quiz/<int:quiz_id>/save-attempt/', views.save_quiz_attempt, name='save_quiz_attempt'),
    path('api/minigame/<int:level_id>/save-attempt/', views.save_minigame_attempt, name='save_minigame_attempt'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

