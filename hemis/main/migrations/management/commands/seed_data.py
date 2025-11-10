# main/management/commands/seed_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import *

class Command(BaseCommand):
    help = 'Test ma\'lumotlarni yaratish'

    def handle(self, *args, **options):
        # Sinflar yaratish
        class_9a = SchoolClass.objects.create(name='9-"A" sinfi', student_count=30)
        class_9b = SchoolClass.objects.create(name='9-"B" sinfi', student_count=28)
        
        # Fanlar yaratish
        math = Subject.objects.create(name='Matematika', teacher_count=4)
        physics = Subject.objects.create(name='Fizika', teacher_count=2)
        english = Subject.objects.create(name='Ingliz tili', teacher_count=5)
        
        self.stdout.write(
            self.style.SUCCESS('Test ma\'lumotlar muvaffaqiyatli yaratildi!')
        )