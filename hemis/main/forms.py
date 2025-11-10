# main/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Student, Teacher, SchoolClass, Subject,Schedule,Announcement

class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if self.instance.pk is None and not password:  # Yangi foydalanuvchi
            raise forms.ValidationError("Parol kiritish majburiy!")
        
        if password and password != confirm_password:
            raise forms.ValidationError("Parollar mos kelmadi!")
        
        return cleaned_data

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['school_class', 'phone_number']
        widgets = {
            'school_class': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['subjects', 'phone_number']
        widgets = {
            'subjects': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agar kerak bo'lsa, qo'shimcha sozlamalar

class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masalan: 9-"A" sinfi'
            }),
        }
        labels = {
            'name': 'Sinf nomi'
        }

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Masalan: Matematika'
            }),
        }
        labels = {
            'name': 'Fan nomi'
        }

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['school_class', 'subject', 'teacher', 'day', 'period', 'room', 'notes']
        widgets = {
            'school_class': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'day': forms.Select(attrs={'class': 'form-select'}),
            'period': forms.Select(attrs={'class': 'form-select'}),
            'room': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Xona raqami'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Qo\'shimcha izohlar...'}),
        }
        labels = {
            'school_class': 'Sinf',
            'subject': 'Fan',
            'teacher': "O'qituvchi",
            'day': 'Hafta kuni',
            'period': 'Dars raqami',
            'room': 'Xona raqami',
            'notes': 'Qo\'shimcha ma\'lumotlar',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # O'qituvchilar ro'yxatini tekshiramiz
        print("Teachers in form:", self.fields['teacher'].queryset.count())

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'announcement_type', 'priority', 
                 'target_class', 'target_subject', 'expiry_date', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E\'lon sarlavhasi'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'E\'lon matni'}),
            'announcement_type': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'target_class': forms.Select(attrs={'class': 'form-select'}),
            'target_subject': forms.Select(attrs={'class': 'form-select'}),
            'expiry_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['target_class'].queryset = SchoolClass.objects.all()
        self.fields['target_subject'].queryset = Subject.objects.all()
        self.fields['target_class'].required = False
        self.fields['target_subject'].required = False
        self.fields['expiry_date'].required = False

class TeacherAnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'announcement_type', 'priority', 
                 'target_class', 'target_subject', 'expiry_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E\'lon sarlavhasi'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'E\'lon matni'}),
            'announcement_type': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'target_class': forms.Select(attrs={'class': 'form-select'}),
            'target_subject': forms.Select(attrs={'class': 'form-select'}),
            'expiry_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        
        if self.teacher:
            # O'qituvchi faqat o'zi o'qitadigan fanlarni tanlashi mumkin
            self.fields['target_subject'].queryset = self.teacher.subjects.all()
            
            # O'qituvchi faqat umumiy yoki fan turidagi e'lon yaratishi mumkin
            self.fields['announcement_type'].choices = [
                ('general', 'Umumiy'),
                ('subject', 'Fan'),
            ]