# main/admin.py
from django.contrib import admin
from .models import *

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'student_count']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher_count']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'school_class', 'phone_number']

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number']
    filter_horizontal = ['subjects']

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'quarter_grade', 'yearly_grade', 'average_score']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'subject']

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'target_class', 'created_at']

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'school_class', 'subject', 'day', 'period', 'room']
    list_filter = ['school_class', 'day', 'period']
    search_fields = ['school_class__name', 'subject__name', 'room']

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'description', 'ip_address', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('description', 'user__username')