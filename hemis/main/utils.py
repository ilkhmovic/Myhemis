# main/utils.py
from .models import ActivityLog,Announcement
from django.utils import timezone
from django.db import models


def log_activity(user, activity_type, description, request=None):
    """Faoliyatni log qilish funksiyasi"""
    ip_address = None
    user_agent = ""
    
    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
    
    ActivityLog.objects.create(
        user=user,
        activity_type=activity_type,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent
    )

def get_client_ip(request):
    """Client IP manzilini olish"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_recent_activities(limit=10):
    """So'nggi faoliyatlarni olish"""
    return ActivityLog.objects.select_related('user').all()[:limit]

def get_user_announcements(user):
    """Foydalanuvchi uchun tegishli e'lonlarni qaytarish"""
    announcements = Announcement.objects.filter(is_active=True)
    
    # Muddat o'tgan e'lonlarni filtrlash
    announcements = announcements.filter(
        models.Q(expiry_date__gte=timezone.now()) | models.Q(expiry_date__isnull=True)
    )
    
    # Adminlar hamma e'lonlarni ko'radi
    if user.is_staff:
        return announcements.select_related('author', 'target_class', 'target_subject').order_by('-created_at')
    
    # O'qituvchilar
    if hasattr(user, 'teacher'):
        teacher = user.teacher
        teacher_announcements = announcements.filter(
            models.Q(author=user) |  # O'z e'lonlari
            models.Q(announcement_type='general') |  # Umumiy e'lonlar
            models.Q(announcement_type='school') |   # Maktab e'lonlari
            models.Q(announcement_type='event') |    # Tadbir e'lonlari
            models.Q(target_subject__in=teacher.subjects.all()) |  # O'qitadigan fanlar
            # O'qituvchining sinflari uchun e'lonlar (agar sinf ma'lumoti bo'lsa)
            models.Q(target_class__isnull=True, target_subject__isnull=True)  # Hech qanday maqsadli emas
        ).distinct()
        return teacher_announcements.select_related('author', 'target_class', 'target_subject').order_by('-created_at')
    
    # O'quvchilar
    if hasattr(user, 'student'):
        student = user.student
        student_class = student.school_class
        
        student_announcements = announcements.filter(
            models.Q(announcement_type='general') |  # Umumiy e'lonlar
            models.Q(announcement_type='school') |   # Maktab e'lonlari
            models.Q(announcement_type='event') |    # Tadbir e'lonlari
            models.Q(target_class=student_class) |   # O'z sinfi e'lonlari
            models.Q(target_class__isnull=True, target_subject__isnull=True)  # Hech qanday maqsadli emas
        ).distinct()
        return student_announcements.select_related('author', 'target_class', 'target_subject').order_by('-created_at')
    
    return Announcement.objects.none()

def create_announcement(author, title, content, announcement_type='general', 
                       priority='medium', target_class=None, target_subject=None, 
                       expiry_date=None):
    """Yangi e'lon yaratish"""
    from .models import Announcement
    
    announcement = Announcement.objects.create(
        author=author,
        title=title,
        content=content,
        announcement_type=announcement_type,
        priority=priority,
        target_class=target_class,
        target_subject=target_subject,
        expiry_date=expiry_date
    )
    
    # Faoliyat tarixiga yozish
    log_activity(
        author,
        'announcement_created',
        f"Yangi e'lon yaratildi: {title}",
        None
    )
    
    return announcement