# main/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.force_logout, name='logout'),
    path('clear-session/', views.clear_session, name='clear_session'),
    
    # Student URLs
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('student/grades/', views.student_grades, name='student_grades'),
    path('student/schedule/', views.student_schedule, name='student_schedule'),
    path('student/attendance/', views.student_attendance, name='student_attendance'),
    path('student/announcements/', views.student_announcements, name='student_announcements'),
    path('student/library/', views.student_library, name='student_library'),
    
    # Teacher URLs
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/grades/', views.teacher_grades, name='teacher_grades'),
    path('teacher/attendance/', views.teacher_attendance, name='teacher_attendance'),
    path('teacher/attendance/save/', views.save_attendance, name='save_attendance'), 
    path('teacher/schedule/', views.teacher_schedule, name='teacher_schedule'),
    path('teacher/announcements/', views.teacher_announcements, name='teacher_announcements'),
    path('teacher/announcements/create/', views.teacher_create_announcement, name='teacher_create_announcement'),
    
    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/add/', views.admin_add_user, name='admin_add_user'),
    path('admin/users/edit/<int:user_id>/', views.admin_edit_user, name='admin_edit_user'),
    path('admin/users/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('admin/users/toggle-active/<int:user_id>/', views.admin_toggle_active, name='admin_toggle_active'),
    path('admin/classes/', views.admin_classes, name='admin_classes'),
    path('admin/reports/', views.admin_reports, name='admin_reports'),
    # Admin e'lon URLlari
    path('admin/announcements/', views.admin_announcements, name='admin_announcements'),
    path('admin/announcements/create/', views.admin_create_announcement, name='admin_create_announcement'),
    path('admin/announcements/<int:announcement_id>/edit/', views.admin_edit_announcement, name='admin_edit_announcement'),
    path('admin/delete-announcement/<int:announcement_id>/', views.admin_delete_announcement, name='admin_delete_announcement'),
    
    # AJAX o'chirish
    path('admin/delete-announcement-ajax/<int:announcement_id>/', views.admin_delete_announcement_ajax, name='admin_delete_announcement_ajax'),

    path('admin/activities/', views.admin_activities, name='admin_activities'),
    path('admin/classes/add-class/', views.admin_add_class, name='admin_add_class'),
    path('admin/classes/edit-class/<int:class_id>/', views.admin_edit_class, name='admin_edit_class'),
    path('admin/classes/delete-class/<int:class_id>/', views.admin_delete_class, name='admin_delete_class'),
    path('admin/classes/add-subject/', views.admin_add_subject, name='admin_add_subject'),
    path('admin/classes/edit-subject/<int:subject_id>/', views.admin_edit_subject, name='admin_edit_subject'),
    path('admin/classes/delete-subject/<int:subject_id>/', views.admin_delete_subject, name='admin_delete_subject'),
        # Dars Jadvali URL lari
    path('admin/schedule/', views.admin_schedule, name='admin_schedule'),
    path('admin/schedule/class/<int:class_id>/', views.admin_schedule_class, name='admin_schedule_class'),
    path('admin/schedule/add/', views.admin_add_schedule, name='admin_add_schedule'),
    path('admin/schedule/edit/<int:schedule_id>/', views.admin_edit_schedule, name='admin_edit_schedule'),
    path('admin/schedule/delete/<int:schedule_id>/', views.admin_delete_schedule, name='admin_delete_schedule'),
]