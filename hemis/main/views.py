# main/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden,JsonResponse
from django.contrib.auth import logout,authenticate,login
from django.contrib import messages
from django.db import transaction, models
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import SchoolClass, Student, Teacher, Subject, ActivityLog,Schedule,Announcement,Attendance
from .forms import UserForm, StudentForm, TeacherForm,SubjectForm,SchoolClassForm,ScheduleForm,TeacherAnnouncementForm,AnnouncementForm
from .utils import log_activity, get_recent_activities ,get_user_announcements # Yangi qo'shildi
from datetime import datetime, timedelta
import json
from django.views.decorators.csrf import csrf_exempt

def home(request):
    """Asosiy sahifa - har doim login qilmagan foydalanuvchiga ko'rinadi"""
    # Agar foydalanuvchi login qilgan bo'lsa, uni o'z sahifasiga yo'naltiramiz
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        elif hasattr(request.user, 'teacher'):
            return redirect('teacher_dashboard')
        elif hasattr(request.user, 'student'):
            return redirect('student_dashboard')
    
    # Login qilmagan foydalanuvchilar uchun home sahifasini ko'rsatamiz
    return render(request, 'home.html')

def force_logout(request):
    """Sessionni to'liq tozalash"""
    # Chiqish faoliyatini log qilish
    if request.user.is_authenticated:
        log_activity(
            request.user,
            'user_logout',
            f"{request.user.username} tizimdan chiqdi (force logout)",
            request
        )
    
    logout(request)
    return redirect('home')

def clear_session(request):
    """Sessionni to'liq tozalash"""
    # Chiqish faoliyatini log qilish
    if request.user.is_authenticated:
        log_activity(
            request.user,
            'user_logout',
            f"{request.user.username} tizimdan chiqdi (clear session)",
            request
        )
    
    logout(request)
    request.session.flush()  # Barcha session ma'lumotlarini tozalash
    return redirect('home')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # ✅ foydalanuvchi to‘g‘ri ma’lumot kiritgan
            login(request, user)

            # 🔥 tizimga kirganini logga yozamiz
            ip = request.META.get('REMOTE_ADDR')
            ua = request.META.get('HTTP_USER_AGENT', '')
            ActivityLog.objects.create(
                user=user,
                activity_type='user_login',
                description=f"{user.username} tizimga kirdi.",
                ip_address=ip,
                user_agent=ua
            )

            return redirect("dashboard")  # yoki sizdagi asosiy sahifa

        else:
            # ❌ foydalanuvchi noto‘g‘ri parol yoki login kiritgan
            ip = request.META.get('REMOTE_ADDR')
            ua = request.META.get('HTTP_USER_AGENT', '')
            ActivityLog.objects.create(
                user=None,
                activity_type='user_status_changed',
                description=f"'{username}' tizimga kirishga urindi, ammo xato.",
                ip_address=ip,
                user_agent=ua
            )

            # ixtiyoriy: xabar ko‘rsatish uchun kontekst
            return render(request, "login.html", {"error": "Login yoki parol xato!"})

    return render(request, "login.html")

def logout_view(request):
    """Logout va faoliyatni log qilish"""
    if request.user.is_authenticated:
        # Chiqish faoliyatini log qilish
        log_activity(
            request.user,
            'user_logout',
            f"{request.user.username} tizimdan chiqdi",
            request
        )
    
    logout(request)
    messages.success(request, "Siz tizimdan muvaffaqiyatli chiqdingiz!")
    return redirect('home')

# Student Views
@login_required
def student_dashboard(request):
    if not hasattr(request.user, 'student'):
        return redirect('home')
    
    # ✅ E'lonlarni qo'shamiz
    recent_announcements = get_user_announcements(request.user)[:5]  # So'nggi 5 ta e'lon
    
    return render(request, 'student/index.html', {
        'recent_announcements': recent_announcements  # ✅ Qo'shildi
    })

@login_required
def student_grades(request):
    if not hasattr(request.user, 'student'):
        return redirect('home')
    return render(request, 'student/baholar.html')

@login_required
def student_schedule(request):
    if not hasattr(request.user, 'student'):
        return redirect('home')
    return render(request, 'student/jadval.html')

@login_required
def student_attendance(request):
    if not hasattr(request.user, 'student'):
        return redirect('home')
    return render(request, 'student/davomat.html')

@login_required
def student_announcements(request):
    """Student e'lonlari"""
    if not hasattr(request.user, 'student'):
        return redirect('home')
    
    student = request.user.student
    
    # Studentga tegishli e'lonlar
    announcements = get_user_announcements(request.user)
    
    context = {
        'announcements': announcements,
        'student': student,
    }
    return render(request, 'student/elonlar.html', context)

@login_required
def student_library(request):
    if not hasattr(request.user, 'student'):
        return redirect('home')
    return render(request, 'student/kutubxona.html')

# Teacher Views
@login_required
def teacher_dashboard(request):
    if not hasattr(request.user, 'teacher'):
        return redirect('home')
    
    teacher = request.user.teacher
    
    # ✅ E'lonlarni qo'shamiz
    recent_announcements = get_user_announcements(request.user)[:5]  # So'nggi 5 ta e'lon
    
    context = {
        'teacher': teacher,
        'classes_count': 3,
        'students_count': 90,
        'next_class': {
            'class_name': '9-"A" sinfi',
            'time': '14:00 - 14:45'
        },
        'recent_announcements': recent_announcements  # ✅ Qo'shildi
    }
    return render(request, 'teacher/teacher-index.html', context)

@login_required
def teacher_grades(request):
    if not hasattr(request.user, 'teacher'):
        return redirect('home')
    
    teacher = request.user.teacher
    context = {
        'teacher': teacher,
    }
    return render(request, 'teacher/teacher-grades.html', context)

@login_required
def teacher_attendance(request):
    if not hasattr(request.user, 'teacher'):
        return redirect('home')
    
    teacher = request.user.teacher
    
    # Sana parametrlari
    from datetime import datetime, timedelta
    date_str = request.GET.get('date')
    if date_str:
        try:
            current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            current_date = datetime.now().date()
    else:
        current_date = datetime.now().date()
    
    # Filtr parametrlari
    selected_class_id = request.GET.get('class_id')
    selected_subject_id = request.GET.get('subject_id')
    selected_period = request.GET.get('period')
    
    # O'qituvchining sinflari
    classes = SchoolClass.objects.filter(
        schedule__teacher=teacher
    ).distinct()
    
    # Fanlar
    if selected_class_id:
        subjects = Subject.objects.filter(
            schedule__teacher=teacher,
            schedule__school_class_id=selected_class_id
        ).distinct()
    else:
        subjects = Subject.objects.filter(
            schedule__teacher=teacher
        ).distinct()
    
    # O'quvchilar
    students = []
    if selected_class_id:
        students = Student.objects.filter(
            school_class_id=selected_class_id
        ).select_related('user', 'school_class')
        
        # Davomat ma'lumotlarini qo'shish
        for student in students:
            try:
                attendance = Attendance.objects.filter(
                    student=student,
                    date=current_date,
                    subject_id=selected_subject_id,
                    period=selected_period,
                    teacher=teacher
                ).first()
                
                if attendance:
                    student.attendance_status = attendance.status
                    student.comment = attendance.comment
                    student.last_updated = attendance.updated_at.strftime('%d.%m.%Y %H:%M')
                else:
                    student.attendance_status = 'present'  # Default holat
                    student.comment = ''
                    student.last_updated = '-'
                    
            except Exception as e:
                student.attendance_status = 'present'
                student.comment = ''
                student.last_updated = '-'
    
    # Statistik ma'lumotlar
    total_students = len(students)
    present_count = len([s for s in students if getattr(s, 'attendance_status', 'present') == 'present'])
    absent_with_reason_count = len([s for s in students if getattr(s, 'attendance_status', 'present') == 'absent_with_reason'])
    absent_without_reason_count = len([s for s in students if getattr(s, 'attendance_status', 'present') == 'absent_without_reason'])
    
    # Foizlarni hisoblash
    present_percentage = round((present_count / total_students * 100)) if total_students > 0 else 0
    absent_with_reason_percentage = round((absent_with_reason_count / total_students * 100)) if total_students > 0 else 0
    absent_without_reason_percentage = round((absent_without_reason_count / total_students * 100)) if total_students > 0 else 0
    
    # Oylik statistika (demo)
    monthly_stats = {
        'attendance_rate': 94,
        'absent_without_reason': 2,
        'absent_with_reason': 5,
        'total_days': 22,
        'max_attendance': 18,
        'average_attendance': 15,
    }
    
    # Sana navigatsiyasi
    prev_date = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
    next_date = (current_date + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # O'zbek tilida oy nomlari
    month_names = {
        1: 'Yanvar', 2: 'Fevral', 3: 'Mart', 4: 'Aprel',
        5: 'May', 6: 'Iyun', 7: 'Iyul', 8: 'Avgust',
        9: 'Sentabr', 10: 'Oktabr', 11: 'Noyabr', 12: 'Dekabr'
    }
    
    # O'zbek tilida kun nomlari
    day_names = {
        'Monday': 'Dushanba',
        'Tuesday': 'Seshanba', 
        'Wednesday': 'Chorshanba',
        'Thursday': 'Payshanba',
        'Friday': 'Juma',
        'Saturday': 'Shanba',
        'Sunday': 'Yakshanba'
    }
    
    current_day_name = day_names.get(current_date.strftime('%A'), current_date.strftime('%A'))
    current_month_name = month_names.get(current_date.month, current_date.strftime('%B'))
    
    context = {
        'teacher': teacher,
        'current_date': current_date,
        'prev_date': prev_date,
        'next_date': next_date,
        'classes': classes,
        'subjects': subjects,
        'students': students,
        'selected_class_id': selected_class_id,
        'selected_subject_id': selected_subject_id,
        'selected_period': selected_period,
        'selected_class': classes.filter(id=selected_class_id).first() if selected_class_id else None,
        'selected_subject': subjects.filter(id=selected_subject_id).first() if selected_subject_id else None,
        'periods': [
            {'number': 1, 'time_slot': '08:00-08:45'},
            {'number': 2, 'time_slot': '09:00-09:45'},
            {'number': 3, 'time_slot': '10:00-10:45'},
            {'number': 4, 'time_slot': '11:00-11:45'},
        ],
        'present_count': present_count,
        'absent_with_reason_count': absent_with_reason_count,
        'absent_without_reason_count': absent_without_reason_count,
        'present_percentage': present_percentage,
        'absent_with_reason_percentage': absent_with_reason_percentage,
        'absent_without_reason_percentage': absent_without_reason_percentage,
        'monthly_stats': monthly_stats,
        'current_month': current_month_name,
        'current_day_name': current_day_name,
    }
    
    return render(request, 'teacher/teacher-attendance.html', context)

@login_required
@csrf_exempt
def save_attendance(request):
    """Davomat ma'lumotlarini saqlash"""
    if request.method == 'POST':
        try:
            # JSON ma'lumotlarini o'qish
            data = json.loads(request.body.decode('utf-8'))
            date_str = data.get('date')
            class_id = data.get('class_id')
            subject_id = data.get('subject_id')
            period = data.get('period')
            attendance_data = data.get('attendance_data', [])
            
            print(f"Saqlash so'rovi: {data}")  # Debug uchun
            
            # Sana formatini o'zgartirish
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            saved_count = 0
            
            # Har bir o'quvchi uchun davomatni saqlash
            for item in attendance_data:
                student_id = item.get('student_id')
                status = item.get('status')
                comment = item.get('comment', '')
                
                # O'quvchini topish
                try:
                    student = Student.objects.get(id=student_id)
                    
                    # Fan va sinfni tekshirish
                    subject = None
                    if subject_id:
                        subject = Subject.objects.get(id=subject_id)
                    
                    # Davomat yaratish yoki yangilash
                    attendance, created = Attendance.objects.update_or_create(
                        student=student,
                        date=date,
                        subject=subject,
                        period=period if period else None,
                        defaults={
                            'status': status,
                            'comment': comment,
                            'teacher': request.user.teacher
                        }
                    )
                    
                    saved_count += 1
                    print(f"Saqlandi: {student.user.get_full_name()} - {status}")
                    
                except Student.DoesNotExist:
                    print(f"O'quvchi topilmadi: {student_id}")
                    continue
                except Subject.DoesNotExist:
                    print(f"Fan topilmadi: {subject_id}")
                    continue
                except Exception as e:
                    print(f"Xatolik: {str(e)}")
                    continue
            
            return JsonResponse({
                'success': True, 
                'message': f'{saved_count} ta davomat saqlandi',
                'saved_count': saved_count
            })
            
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False, 
                'error': f'JSON dekodlash xatosi: {str(e)}'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': f'Saqlashda xatolik: {str(e)}'
            })
    
    return JsonResponse({
        'success': False, 
        'error': 'Noto\'g\'ri so\'rov usuli. Faqat POST so\'rovi qabul qilinadi.'
    })

def get_monthly_stats(teacher, current_date):
    # Oylik statistikani hisoblash
    start_of_month = current_date.replace(day=1)
    if current_date.month == 12:
        end_of_month = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
    
    # Demo ma'lumotlar - haqiqiy loyihada database dan olinadi
    return {
        'attendance_rate': 94,
        'absent_without_reason': 2,
        'absent_with_reason': 5,
        'total_days': 22,
        'max_attendance': 18,
        'average_attendance': 15,
    }
def teacher_schedule(request):
    teacher = request.user.teacher
    
    # Hafta parametrini olish
    week_offset = int(request.GET.get('week', 0))
    
    # Joriy sanani olish
    today = timezone.now().date()
    
    # Hafta boshi (Dushanba) ni hisoblash
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    
    # Hafta oxiri (Yakshanba) ni hisoblash
    end_of_week = start_of_week + timedelta(days=6)
    
    # Hafta raqamini hisoblash
    week_number = start_of_week.isocalendar()[1]
    
    # O'zbek tilida oy nomlari
    month_names = {
        1: 'Yanvar', 2: 'Fevral', 3: 'Mart', 4: 'Aprel',
        5: 'May', 6: 'Iyun', 7: 'Iyul', 8: 'Avgust',
        9: 'Sentabr', 10: 'Oktabr', 11: 'Noyabr', 12: 'Dekabr'
    }
    
    # Hafta oralig'ini formatlash
    if start_of_week.month == end_of_week.month:
        week_dates = f"{start_of_week.day}-{end_of_week.day} {month_names[start_of_week.month]} {start_of_week.year}"
    else:
        week_dates = f"{start_of_week.day} {month_names[start_of_week.month]} - {end_of_week.day} {month_names[end_of_week.month]} {start_of_week.year}"
    
    # O'qituvchining dars jadvalini olish
    schedules = Schedule.objects.filter(teacher=teacher).select_related(
        'school_class', 'subject'
    )
    
    # Kunlar bo'yicha guruhlash
    schedule_data = {
        'monday': schedules.filter(day='monday').order_by('period'),
        'tuesday': schedules.filter(day='tuesday').order_by('period'),
        'wednesday': schedules.filter(day='wednesday').order_by('period'),
        'thursday': schedules.filter(day='thursday').order_by('period'),
        'friday': schedules.filter(day='friday').order_by('period'),
        'saturday': schedules.filter(day='saturday').order_by('period'),
    }
    
    # Dars soatlari
    periods = [
        {'number': 1, 'time_slot': '08:00-08:45'},
        {'number': 2, 'time_slot': '09:00-09:45'},
        {'number': 3, 'time_slot': '10:00-10:45'},
        {'number': 4, 'time_slot': '11:00-11:45'},
        {'number': 5, 'time_slot': '12:00-12:45'},
        {'number': 6, 'time_slot': '13:00-13:45'},
        {'number': 7, 'time_slot': '14:00-14:45'},
        {'number': 8, 'time_slot': '15:00-15:45'},
    ]
    
    # Bugungi darslar
    today_name = today.strftime('%A').lower()
    today_lessons = schedules.filter(day=today_name).order_by('period')
    
    # Joriy darsni aniqlash
    current_time = timezone.now().time()
    for lesson in today_lessons:
        lesson_time = datetime.strptime(lesson.time_slot.split('-')[0], '%H:%M').time()
        lesson.is_current = (lesson_time <= current_time)
    
    # Statistik ma'lumotlar
    weekly_lessons_count = schedules.count()
    classes_count = schedules.values('school_class').distinct().count()
    subjects_count = schedules.values('subject').distinct().count()
    weekly_hours = round(weekly_lessons_count * 0.75, 1)
    
    context = {
        'teacher': teacher,
        'schedule_data': schedule_data,
        'periods': periods,
        'today_lessons': today_lessons,
        'current_week_dates': week_dates,
        'current_week_number': week_number,
        'current_week_offset': week_offset,
        'weekly_lessons_count': weekly_lessons_count,
        'classes_count': classes_count,
        'subjects_count': subjects_count,
        'weekly_hours': weekly_hours,
        'empty_slots_count': len(periods) * 6 - weekly_lessons_count,
        'busiest_day_count': max([schedule_data[day].count() for day in schedule_data]),
    }
    
    return render(request, 'teacher/teacher-schedule.html', context)

@login_required
def teacher_announcements(request):
    """O'qituvchi e'lonlari"""
    if not hasattr(request.user, 'teacher'):
        return redirect('home')
    
    teacher = request.user.teacher
    
    # O'qituvchining e'lonlari
    my_announcements = Announcement.objects.filter(author=request.user)
    
    # O'qituvchiga tegishli e'lonlar
    relevant_announcements = get_user_announcements(request.user)
    
    context = {
        'teacher': teacher,
        'my_announcements': my_announcements,
        'relevant_announcements': relevant_announcements,
    }
    return render(request, 'teacher/teacher-announcements.html', context)

@login_required
def teacher_create_announcement(request):
    """O'qituvchi yangi e'lon yaratish"""
    if not hasattr(request.user, 'teacher'):
        return redirect('home')
    
    teacher = request.user.teacher
    
    if request.method == 'POST':
        form = TeacherAnnouncementForm(request.POST, teacher=teacher)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.author = request.user
            
            # O'qituvchi e'lonini tekshirish
            if announcement.target_subject and announcement.target_subject not in teacher.subjects.all():
                messages.error(request, 'Siz faqat o\'zingiz o\'qitadigan fanlar uchun e\'lon yarata olasiz!')
                return redirect('teacher_create_announcement')
            
            announcement.save()
            
            # Faoliyat tarixiga yozish
            log_activity(
                request.user,
                'announcement_created',
                f"O'qituvchi tomonidan yangi e'lon yaratildi: {announcement.title}",
                request
            )
            
            messages.success(request, 'E\'lon muvaffaqiyatli yaratildi!')
            return redirect('teacher_announcements')
    else:
        form = TeacherAnnouncementForm(teacher=teacher)
    
    context = {
        'teacher': teacher,
        'form': form,
    }
    return render(request, 'teacher/teacher-create-announcement.html', context)


def admin_required(function):
    """Admin huquqlarini tekshirish uchun dekorator"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')
        if not request.user.is_staff:
            return HttpResponseForbidden("Sizga bu sahifani ko'rish uchun ruxsat yo'q")
        return function(request, *args, **kwargs)
    return wrapper

# Admin Views
@login_required
@admin_required
def admin_dashboard(request):
    """Admin asosiy sahifasi"""
    # Statistik ma'lumotlarni hisoblash
    students_count = Student.objects.count()
    teachers_count = Teacher.objects.count()
    classes_count = SchoolClass.objects.count()
    
    # So'nggi faoliyatlarni olish
    recent_activities = get_recent_activities(5)
    
    context = {
        'students_count': students_count,
        'teachers_count': teachers_count,
        'classes_count': classes_count,
        'recent_activities': recent_activities,
    }
    return render(request, 'admin/admin-index.html', context)

@login_required
@admin_required
def admin_users(request):
    """Barcha foydalanuvchilarni ko'rsatish"""
    students = Student.objects.select_related('user', 'school_class').all()
    teachers = Teacher.objects.select_related('user').prefetch_related('subjects').all()
    
    context = {
        'students': students,
        'teachers': teachers,
    }
    return render(request, 'admin/admin-users.html', context)


@login_required
@admin_required
def admin_reports(request):
    """Hisobotlar"""
    return render(request, 'admin/admin-reports.html')



@login_required
@admin_required
def admin_add_user(request):
    """Yangi foydalanuvchi qo'shish"""
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        user_type = request.POST.get('user_type')
        
        if user_form.is_valid():
            try:
                with transaction.atomic():
                    user = user_form.save(commit=False)
                    user.set_password(request.POST.get('password'))
                    user.save()
                    
                    if user_type == 'student':
                        student_form = StudentForm(request.POST)
                        if student_form.is_valid():
                            student = student_form.save(commit=False)
                            student.user = user
                            student.save()
                            # Activity log
                            log_activity(
                                request.user, 
                                'user_created', 
                                f"Yangi o'quvchi qo'shildi: {user.get_full_name()} ({user.username})",
                                request
                            )
                            messages.success(request, 'Oʻquvchi muvaffaqiyatli qoʻshildi!')
                        else:
                            user.delete()
                            messages.error(request, 'Oʻquvchi maʼlumotlarida xatolik!')
                    
                    elif user_type == 'teacher':
                        teacher_form = TeacherForm(request.POST)
                        if teacher_form.is_valid():
                            teacher = teacher_form.save(commit=False)
                            teacher.user = user
                            teacher.save()
                            teacher_form.save_m2m()  # Many-to-many bogʻlanishlar uchun
                            # Activity log
                            log_activity(
                                request.user, 
                                'user_created', 
                                f"Yangi o'qituvchi qo'shildi: {user.get_full_name()} ({user.username})",
                                request
                            )
                            messages.success(request, 'Oʻqituvchi muvaffaqiyatli qoʻshildi!')
                        else:
                            user.delete()
                            messages.error(request, 'Oʻqituvchi maʼlumotlarida xatolik!')
                    
                    return redirect('admin_users')
                    
            except Exception as e:
                messages.error(request, f'Xatolik yuz berdi: {str(e)}')
    else:
        user_form = UserForm()
    
    classes = SchoolClass.objects.all()
    subjects = Subject.objects.all()
    
    context = {
        'user_form': user_form,
        'classes': classes,
        'subjects': subjects,
    }
    return render(request, 'admin/admin-add-user.html', context)

@login_required
@admin_required
def admin_edit_user(request, user_id):
    """Foydalanuvchini tahrirlash"""
    user = get_object_or_404(User, id=user_id)
    
    try:
        student = Student.objects.get(user=user)
        user_type = 'student'
    except Student.DoesNotExist:
        student = None
    
    try:
        teacher = Teacher.objects.get(user=user)
        user_type = 'teacher'
    except Teacher.DoesNotExist:
        teacher = None
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        
        if user_form.is_valid():
            user = user_form.save()
            
            if user_type == 'student' and student:
                student_form = StudentForm(request.POST, instance=student)
                if student_form.is_valid():
                    student_form.save()
                    # Activity log
                    log_activity(
                        request.user, 
                        'user_updated', 
                        f"O'quvchi ma'lumotlari yangilandi: {user.get_full_name()} ({user.username})",
                        request
                    )
                    messages.success(request, 'Oʻquvchi maʼlumotlari muvaffaqiyatli yangilandi!')
            
            elif user_type == 'teacher' and teacher:
                teacher_form = TeacherForm(request.POST, instance=teacher)
                if teacher_form.is_valid():
                    # Many-to-many bog'lanishlarni saqlash
                    teacher_instance = teacher_form.save(commit=False)
                    teacher_instance.save()
                    teacher_form.save_m2m()  # Bu yerda to'g'ri ishlaydi
                    
                    # Activity log
                    log_activity(
                        request.user, 
                        'user_updated', 
                        f"O'qituvchi ma'lumotlari yangilandi: {user.get_full_name()} ({user.username})",
                        request
                    )
                    messages.success(request, 'Oʻqituvchi maʼlumotlari muvaffaqiyatli yangilandi!')
            
            return redirect('admin_users')
    
    else:
        user_form = UserForm(instance=user)
    
    classes = SchoolClass.objects.all()
    subjects = Subject.objects.all()
    
    context = {
        'user_form': user_form,
        'user_type': user_type,
        'student': student,
        'teacher': teacher,
        'classes': classes,
        'subjects': subjects,
    }
    return render(request, 'admin/admin-edit-user.html', context)

@login_required
@admin_required
def admin_delete_user(request, user_id):
    """Foydalanuvchini o'chirish"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        # Activity log
        log_activity(
            request.user, 
            'user_deleted', 
            f"Foydalanuvchi o'chirildi: {user.get_full_name()} ({username})",
            request
        )
        messages.success(request, f'Foydalanuvchi "{username}" muvaffaqiyatli oʻchirildi!')
        return redirect('admin_users')
    
    context = {'user': user}
    return render(request, 'admin/admin-delete-user.html', context)

@login_required
@admin_required
def admin_toggle_active(request, user_id):
    """Foydalanuvchi faolligini o'zgartirish"""
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    
    status = "faollashtirildi" if user.is_active else "bloklandi"
    # Activity log
    log_activity(
        request.user, 
        'user_status_changed', 
        f"Foydalanuvchi holati o'zgartirildi: {user.get_full_name()} ({user.username}) - {status}",
        request
    )
    messages.success(request, f'Foydalanuvchi "{user.username}" {status}!')
    return redirect('admin_users')

@login_required
@admin_required
def admin_activities(request):
    """Faoliyat tarixi sahifasi"""
    # Filtrlash parametrlari
    activity_type = request.GET.get('type', 'all')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search = request.GET.get('search', '')
    
    # Faoliyatlarni olish
    activities = ActivityLog.objects.select_related('user').all()
    
    # Filtrlash
    if activity_type != 'all':
        activities = activities.filter(activity_type=activity_type)
    
    if date_from:
        activities = activities.filter(created_at__gte=date_from)
    
    if date_to:
        activities = activities.filter(created_at__lte=date_to)
    
    if search:
        activities = activities.filter(
            models.Q(description__icontains=search) |
            models.Q(user__username__icontains=search) |
            models.Q(user__first_name__icontains=search) |
            models.Q(user__last_name__icontains=search)
        )
    
    # Sahifalash
    page = request.GET.get('page', 1)
    paginator = Paginator(activities, 20)  # Har sahifada 20 ta
    
    try:
        activities_page = paginator.page(page)
    except PageNotAnInteger:
        activities_page = paginator.page(1)
    except EmptyPage:
        activities_page = paginator.page(paginator.num_pages)
    
    context = {
        'activities': activities_page,
        'activity_types': ActivityLog.ACTIVITY_TYPES,
        'current_type': activity_type,
        'date_from': date_from,
        'date_to': date_to,
        'search': search,
    }
    return render(request, 'admin/admin-activities.html', context)

@login_required
@admin_required
def admin_classes(request):
    """Sinflar va fanlar boshqaruvi"""
    classes = SchoolClass.objects.all()
    subjects = Subject.objects.all()
    
    context = {
        'classes': classes,
        'subjects': subjects,
    }
    return render(request, 'admin/admin-classes.html', context)

@login_required
@admin_required
def admin_add_class(request):
    """Yangi sinf qo'shish"""
    if request.method == 'POST':
        form = SchoolClassForm(request.POST)
        if form.is_valid():
            school_class = form.save()
            # Activity log
            log_activity(
                request.user,
                'class_created',
                f"Yangi sinf qo'shildi: {school_class.name}",
                request
            )
            messages.success(request, 'Sinf muvaffaqiyatli qoʻshildi!')
            return redirect('admin_classes')
    else:
        form = SchoolClassForm()
    
    context = {'form': form}
    return render(request, 'admin/admin-add-class.html', context)

@login_required
@admin_required
def admin_edit_class(request, class_id):
    """Sinfni tahrirlash"""
    school_class = get_object_or_404(SchoolClass, id=class_id)
    
    if request.method == 'POST':
        form = SchoolClassForm(request.POST, instance=school_class)
        if form.is_valid():
            form.save()
            # Activity log
            log_activity(
                request.user,
                'class_updated',
                f"Sinf ma'lumotlari yangilandi: {school_class.name}",
                request
            )
            messages.success(request, 'Sinf maʼlumotlari muvaffaqiyatli yangilandi!')
            return redirect('admin_classes')
    else:
        form = SchoolClassForm(instance=school_class)
    
    context = {
        'form': form,
        'school_class': school_class,
    }
    return render(request, 'admin/admin-edit-class.html', context)

@login_required
@admin_required
def admin_delete_class(request, class_id):
    """Sinfni o'chirish"""
    school_class = get_object_or_404(SchoolClass, id=class_id)
    
    if request.method == 'POST':
        class_name = school_class.name
        # Sinfga bog'langan o'quvchilarni tekshirish
        student_count = Student.objects.filter(school_class=school_class).count()
        if student_count > 0:
            messages.error(request, f"Bu sinfda {student_count} ta o'quvchi mavjud. Avval o'quvchilarni boshqa sinfga ko'chiring.")
            return redirect('admin_classes')
        
        school_class.delete()
        # Activity log
        log_activity(
            request.user,
            'class_deleted',
            f"Sinf o'chirildi: {class_name}",
            request
        )
        messages.success(request, f'Sinf "{class_name}" muvaffaqiyatli oʻchirildi!')
        return redirect('admin_classes')
    
    context = {'school_class': school_class}
    return render(request, 'admin/admin-delete-class.html', context)

@login_required
@admin_required
def admin_add_subject(request):
    """Yangi fan qo'shish"""
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()
            # Activity log
            log_activity(
                request.user,
                'subject_created',
                f"Yangi fan qo'shildi: {subject.name}",
                request
            )
            messages.success(request, 'Fan muvaffaqiyatli qoʻshildi!')
            return redirect('admin_classes')
    else:
        form = SubjectForm()
    
    context = {'form': form}
    return render(request, 'admin/admin-add-subject.html', context)

@login_required
@admin_required
def admin_edit_subject(request, subject_id):
    """Fanni tahrirlash"""
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            # Activity log
            log_activity(
                request.user,
                'subject_updated',
                f"Fan ma'lumotlari yangilandi: {subject.name}",
                request
            )
            messages.success(request, 'Fan maʼlumotlari muvaffaqiyatli yangilandi!')
            return redirect('admin_classes')
    else:
        form = SubjectForm(instance=subject)
    
    context = {
        'form': form,
        'subject': subject,
    }
    return render(request, 'admin/admin-edit-subject.html', context)

@login_required
@admin_required
def admin_delete_subject(request, subject_id):
    """Fanni o'chirish"""
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        subject_name = subject.name
        # Fanga bog'langan o'qituvchilarni tekshirish
        teacher_count = Teacher.objects.filter(subjects=subject).count()
        if teacher_count > 0:
            messages.error(request, f"Bu fan {teacher_count} ta o'qituvchiga bog'langan. Avval o'qituvchilardan fanni olib tashlang.")
            return redirect('admin_classes')
        
        subject.delete()
        # Activity log
        log_activity(
            request.user,
            'subject_deleted',
            f"Fan o'chirildi: {subject_name}",
            request
        )
        messages.success(request, f'Fan "{subject_name}" muvaffaqiyatli oʻchirildi!')
        return redirect('admin_classes')
    
    context = {'subject': subject}
    return render(request, 'admin/admin-delete-subject.html', context)

@login_required
@admin_required
def admin_schedule(request):
    """Barcha sinflar ro'yxati"""
    classes = SchoolClass.objects.all()
    
    context = {
        'classes': classes,
    }
    return render(request, 'admin/admin-schedule.html', context)

@login_required
@admin_required
def admin_add_schedule(request):
    # URL dan class_id ni olish
    class_id = request.GET.get('class_id')
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        print("POST data:", request.POST)  # DEBUG
        
        if form.is_valid():
            try:
                schedule = form.save()
                messages.success(request, 'Dars muvaffaqiyatli qo\'shildi!')
                # Agar class_id bo'lsa, shu sinfning jadvaliga qaytamiz
                if class_id:
                    return redirect('admin_schedule_class', class_id=class_id)
                else:
                    return redirect('admin_schedule')
            except Exception as e:
                messages.error(request, f'Xatolik yuz berdi: {str(e)}')
        else:
            print("Form errors:", form.errors)  # DEBUG
            messages.error(request, 'Iltimos, formani to\'g\'ri to\'ldiring!')
    else:
        # Agar class_id bo'lsa, avval o'sha sinfni tanlab qo'yamiz
        initial_data = {}
        if class_id:
            try:
                school_class = SchoolClass.objects.get(id=class_id)
                initial_data['school_class'] = school_class
            except SchoolClass.DoesNotExist:
                pass
        
        form = ScheduleForm(initial=initial_data)
    
    context = {
        'form': form,
        'classes': SchoolClass.objects.all(),
        'subjects': Subject.objects.all(),
        'teachers': Teacher.objects.all(),
        'current_class_id': class_id,  # Template ga yuboramiz
        'current_class': SchoolClass.objects.get(id=class_id) if class_id else None,
    }
    
    return render(request, 'admin/admin-add-schedule.html', context)

@login_required
@admin_required
def admin_edit_schedule(request, schedule_id):
    try:
        schedule = Schedule.objects.get(id=schedule_id)
    except Schedule.DoesNotExist:
        messages.error(request, 'Dars topilmadi!')
        return redirect('admin_schedule')
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            try:
                updated_schedule = form.save()
                messages.success(request, 'Dars muvaffaqiyatli yangilandi!')
                return redirect('admin_schedule_class', class_id=updated_schedule.school_class.id)
            except Exception as e:
                messages.error(request, f'Xatolik yuz berdi: {str(e)}')
        else:
            messages.error(request, 'Iltimos, formani to\'g\'ri to\'ldiring!')
    else:
        form = ScheduleForm(instance=schedule)
    
    context = {
        'form': form,
        'schedule': schedule,
        'classes': SchoolClass.objects.all(),
        'subjects': Subject.objects.all(),
        'teachers': Teacher.objects.all(),
        'current_class': schedule.school_class,  # Tahrirlanayotgan darsning sinfi
    }
    
    return render(request, 'admin/admin-edit-schedule.html', context)

@login_required
@admin_required
def admin_delete_schedule(request, schedule_id):
    try:
        schedule = Schedule.objects.get(id=schedule_id)
    except Schedule.DoesNotExist:
        messages.error(request, 'Dars topilmadi!')
        return redirect('admin_schedule')
    
    if request.method == 'POST':
        class_id = schedule.school_class.id
        schedule_title = f"{schedule.school_class.name} - {schedule.subject.name} - {schedule.get_day_display()} {schedule.period}-dars"
        schedule.delete()
        messages.success(request, f'"{schedule_title}" darsi muvaffaqiyatli o\'chirildi!')
        return redirect('admin_schedule_class', class_id=class_id)
    
    context = {
        'schedule': schedule,
    }
    
    return render(request, 'admin/admin-delete-schedule.html', context)

@login_required
@admin_required
def admin_schedule_class(request, class_id):
    """Ma'lum bir sinfning dars jadvali"""
    try:
        school_class = SchoolClass.objects.get(id=class_id)
    except SchoolClass.DoesNotExist:
        messages.error(request, 'Sinf topilmadi!')
        return redirect('admin_schedule')
    
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    lessons = [1, 2, 3, 4, 5, 6, 7, 8]
    
    # Faqat shu sinfning darslarini olamiz
    schedules = Schedule.objects.filter(school_class=school_class).select_related(
        'subject', 'teacher__user'
    )
    
    # Ma'lumotlarni tashkil etish
    schedule_data = {}
    for day in days:
        schedule_data[day] = {}
        for lesson in lessons:
            schedule_data[day][lesson] = None
    
    for schedule in schedules:
        if (schedule.day in schedule_data and 
            schedule.period in schedule_data[schedule.day]):
            schedule_data[schedule.day][schedule.period] = schedule
    
    context = {
        'school_class': school_class,
        'days': days,
        'lessons': lessons,
        'schedule_data': schedule_data,
    }
    
    return render(request, 'admin/admin-view-schedule.html', context)

@login_required
@admin_required
def admin_announcements(request):
    """Admin e'lonlar boshqaruvi"""
    announcements = Announcement.objects.select_related('author', 'target_class', 'target_subject').all()
    
    # Filtrlash
    announcement_type = request.GET.get('type', 'all')
    if announcement_type != 'all':
        announcements = announcements.filter(announcement_type=announcement_type)
    
    status = request.GET.get('status', 'all')
    if status == 'active':
        announcements = announcements.filter(is_active=True)
    elif status == 'expired':
        announcements = announcements.filter(expiry_date__lt=timezone.now())
    elif status == 'inactive':
        announcements = announcements.filter(is_active=False)
    
    context = {
        'announcements': announcements,
        'announcement_types': Announcement.ANNOUNCEMENT_TYPES,
        'current_type': announcement_type,
        'current_status': status,
    }
    return render(request, 'admin/admin-announcements.html', context)

@login_required
@admin_required
def admin_create_announcement(request):
    """Yangi e'lon yaratish (admin)"""
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.author = request.user
            
            # Agar hech qanday maqsad tanlanmagan bo'lsa, umumiy e'lon deb belgilash
            if not announcement.target_class and not announcement.target_subject:
                announcement.announcement_type = 'general'
            
            announcement.save()
            
            # Faoliyat tarixiga yozish
            log_activity(
                request.user,
                'announcement_created',
                f"Admin tomonidan yangi e'lon yaratildi: {announcement.title}",
                request
            )
            
            messages.success(request, 'E\'lon muvaffaqiyatli yaratildi!')
            return redirect('admin_announcements')
    else:
        form = AnnouncementForm()
    
    context = {
        'form': form,
        'classes': SchoolClass.objects.all(),
        'subjects': Subject.objects.all(),
    }
    return render(request, 'admin/admin-create-announcement.html', context)

@login_required
@admin_required
def admin_edit_announcement(request, announcement_id):
    # E'lonni topish yoki 404 xatosi
    announcement = get_object_or_404(Announcement, id=announcement_id)
    
    if request.method == 'POST':
        # Formani tekshirish
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'E\'lon muvaffaqiyatli yangilandi!')
            return redirect('admin_announcements')  # E'lonlar ro'yxatiga qaytish
    else:
        # Formani mavjud ma'lumotlar bilan to'ldirish
        form = AnnouncementForm(instance=announcement)
    
    return render(request, 'admin/edit-announcement.html', {
        'form': form,
        'announcement': announcement
    })

@login_required
@admin_required
def admin_delete_announcement(request, announcement_id):
    """
    E'lonni o'chirish funksiyasi
    """
    try:
        # E'lonni topish
        announcement = get_object_or_404(Announcement, id=announcement_id)
        
        # E'lonni o'chirish
        announcement_title = announcement.title
        announcement.delete()
        
        # Muvaffaqiyat xabari
        messages.success(request, f'"{announcement_title}" e\'loni muvaffaqiyatli o\'chirildi!')
        
    except Exception as e:
        # Xato xabari
        messages.error(request, f'E\'loni o\'chirishda xato: {str(e)}')
    
    # E'lonlar ro'yxatiga qaytish
    return redirect('admin_announcements')

def admin_delete_announcement_ajax(request, announcement_id):
    """
    AJAX orqali e'lonni o'chirish
    """
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            announcement = get_object_or_404(Announcement, id=announcement_id)
            announcement_title = announcement.title
            announcement.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'"{announcement_title}" e\'loni o\'chirildi'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Xato: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Noto\'g\'ri so\'rov'})

