# accounts/views.py
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from main.models import Teacher, Student

@login_required
def profile_redirect(request):
    """Login qilgandan keyin foydalanuvchini o'z sahifasiga yo'naltiradi"""
    print(f"DEBUG: Foydalanuvchi: {request.user.username}, Staff: {request.user.is_staff}")
    
    # Admin tekshiruvi
    if request.user.is_staff:
        print("DEBUG: Admin sahifasiga yo'naltirilmoqda")
        return redirect('admin_dashboard')
    
    # O'qituvchi tekshiruvi
    try:
        teacher = Teacher.objects.get(user=request.user)
        print(f"DEBUG: O'qituvchi topildi: {teacher.user.username}")
        return redirect('teacher_dashboard')
    except Teacher.DoesNotExist:
        print("DEBUG: O'qituvchi topilmadi")
        pass
    
    # O'quvchi tekshiruvi
    try:
        student = Student.objects.get(user=request.user)
        print(f"DEBUG: O'quvchi topildi: {student.user.username}")
        return redirect('student_dashboard')
    except Student.DoesNotExist:
        print("DEBUG: O'quvchi topilmadi")
        pass
    
    # Agar hech qaysi profil topilmasa
    print("DEBUG: Hech qanday profil topilmadi, home sahifasiga qaytish")
    return redirect('home')