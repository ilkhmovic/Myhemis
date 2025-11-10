# main/models.py
from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone

# Barcha modelar standart User ga reference qilishi kerak
class SchoolClass(models.Model):
    name = models.CharField(max_length=50)
    student_count = models.IntegerField(default=0)
    
    def __str__(self):
#Dars Jadvalini Ko'rish
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    teacher_count = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subjects = models.ManyToManyField(Subject)
    phone_number = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    quarter_grade = models.IntegerField(null=True, blank=True)
    yearly_grade = models.IntegerField(null=True, blank=True)
    average_score = models.FloatField(default=0.0)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student} - {self.subject}: {self.quarter_grade}"

class Attendance(models.Model):
    ATTENDANCE_CHOICES = [
        ('present', 'Keldi'),
        ('absent_with_reason', 'Sababli'),
        ('absent_without_reason', 'Sababsiz'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    period = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=25, choices=ATTENDANCE_CHOICES, default='present')
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'date', 'subject', 'period']
        ordering = ['date', 'student']
    
    def __str__(self):
        return f"{self.student} - {self.date} - {self.get_status_display()}"

class Announcement(models.Model):
    ANNOUNCEMENT_TYPES = [
        ('school', 'Maktab'),
        ('class', 'Sinf'),
        ('subject', 'Fan'),
        ('event', 'Tadbir'),
        ('general', 'Umumiy'),
    ]
    
    PRIORITY_LEVELS = [
        ('high', 'Yuqori'),
        ('medium', 'O\'rta'),
        ('low', 'Past'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    content = models.TextField(verbose_name="Matn")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Muallif")
    announcement_type = models.CharField(max_length=20, choices=ANNOUNCEMENT_TYPES, default='general', verbose_name="E'lon turi")
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium', verbose_name="Muhimlik")
    
    # Qabul qiluvchilar
    target_class = models.ForeignKey('SchoolClass', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Maqsadli sinf")
    target_subject = models.ForeignKey('Subject', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Maqsadli fan")
    
    # Vaqt chegaralari
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    expiry_date = models.DateTimeField(null=True, blank=True, verbose_name="Muddati")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "E'lon"
        verbose_name_plural = "E'lonlar"
        ordering = ['-created_at']
    
    def get_priority_class(self):
        """CSS classini olish"""
        return f"priority-{self.priority}"
    
    def is_expired(self):
        """Muddati o'tganligini tekshirish"""
        if self.expiry_date:
            return timezone.now() > self.expiry_date
        return False
    
    def can_view(self, user):
        """Foydalanuvchi e'loni ko'ra olishini tekshirish"""
        if not self.is_active or self.is_expired():
            return False
            
        # Adminlar hamma e'lonlarni ko'ra oladi
        if user.is_staff:
            return True
            
        # O'qituvchilar
        if hasattr(user, 'teacher'):
            # O'z e'lonlari
            if self.author == user:
                return True
            # O'qitadigan fanlar bo'yicha e'lonlar
            if self.target_subject and self.target_subject in user.teacher.subjects.all():
                return True
            # O'qitadigan sinflar bo'yicha e'lonlar
            if self.target_class:
                # Bu yerda o'qituvchining sinflarini aniqlash logikasi
                return True
            # Umumiy e'lonlar
            if self.announcement_type == 'general':
                return True
                
        # O'quvchilar
        if hasattr(user, 'student'):
            # O'z sinfi e'lonlari
            if self.target_class and self.target_class == user.student.school_class:
                return True
            # O'qiydigan fanlar bo'yicha e'lonlar
            if self.target_subject:
                # Bu yerda o'quvchining fanlarini tekshirish
                return True
            # Umumiy e'lonlar
            if self.announcement_type == 'general':
                return True
                
        return False

class Schedule(models.Model):
    DAY_CHOICES = [
        ('monday', 'Dushanba'),
        ('tuesday', 'Seshanba'),
        ('wednesday', 'Chorshanba'),
        ('thursday', 'Payshanba'),
        ('friday', 'Juma'),
        ('saturday', 'Shanba'),
    ]
    
    school_class = models.ForeignKey('SchoolClass', on_delete=models.CASCADE, verbose_name="Sinf")
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, verbose_name="Fan")
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE, verbose_name="O'qituvchi")  # YANGI MAYDON
    day = models.CharField(max_length=20, choices=DAY_CHOICES, verbose_name="Hafta kuni")
    period = models.IntegerField(
        verbose_name="Dars raqami", 
        choices=[(i, f"{i}-dars") for i in range(1, 9)],
        default=1
    )
    room = models.CharField(max_length=20, verbose_name="Xona")
    notes = models.TextField(blank=True, null=True, verbose_name="Izohlar")
    
    def __str__(self):
        return f"{self.school_class.name} - {self.subject.name} - {self.teacher.user.get_full_name()} - {self.get_day_display()} {self.period}-dars"
    
    class Meta:
        verbose_name = "Dars jadvali"
        verbose_name_plural = "Dars jadvali"
        constraints = [
            # Bitta o'qituvchi bir vaqtda 2 joyda bo'lmasligi uchun
            models.UniqueConstraint(
                fields=['teacher', 'day', 'period'],
                name='unique_teacher_schedule'
            ),
            # Bitta xonada bir vaqtda 2 dars bo'lmasligi uchun
            models.UniqueConstraint(
                fields=['room', 'day', 'period'],
                name='unique_room_schedule'
            ),
            # Bitta sinfda bir vaqtda 2 dars bo'lmasligi uchun
            models.UniqueConstraint(
                fields=['school_class', 'day', 'period'],
                name='unique_class_schedule'
            ),
        ]

class ActivityLog(models.Model):
    ACTIVITY_TYPES = [
        ('user_login', 'Foydalanuvchi tizimga kirdi'),
        ('user_logout', 'Foydalanuvchi tizimdan chiqdi'),
        ('user_created', 'Yangi foydalanuvchi yaratildi'),
        ('user_updated', 'Foydalanuvchi ma\'lumotlari yangilandi'),
        ('user_deleted', 'Foydalanuvchi o\'chirildi'),
        ('user_status_changed', 'Foydalanuvchi holati o\'zgartirildi'),
        ('class_created', 'Yangi sinf yaratildi'),
        ('class_updated', 'Sinf ma\'lumotlari yangilandi'),
        ('class_deleted', 'Sinf o\'chirildi'),
        ('subject_created', 'Yangi fan yaratildi'),
        ('subject_updated', 'Fan ma\'lumotlari yangilandi'),
        ('subject_deleted', 'Fan o\'chirildi'),
        ('announcement_created', 'Yangi e\'lon yaratildi'),
        ('announcement_updated', 'E\'lon yangilandi'),
        ('announcement_deleted', 'E\'lon o\'chirildi'),
        ('schedule_updated', 'Dars jadvali yangilandi'),
        ('report_generated', 'Hisobot yaratildi'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Faoliyat tarixi'
        verbose_name_plural = 'Faoliyat tarixi'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} - {self.created_at}"
    
def user_role(self):
    if hasattr(self, 'teacher'):
        return 'teacher'
    elif hasattr(self, 'student'):
        return 'student'
    else:
        return 'other'

User.add_to_class('role', property(user_role))