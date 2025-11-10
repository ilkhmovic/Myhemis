from .utils import get_user_announcements
from django.utils import timezone

def announcements_processor(request):
    """Barcha sahifalarga e'lonlarni qo'shish"""
    if request.user.is_authenticated:
        announcements = get_user_announcements(request.user)
        recent_announcements = announcements[:5]  # So'nggi 5 ta e'lon
    else:
        announcements = []
        recent_announcements = []
    
    return {
        'recent_announcements': recent_announcements,
        'user_announcements': announcements
    }