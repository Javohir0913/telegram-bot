import re
import os

tillar = ['Uz', 'kril', 'Ru']
OPTIMAL_QUALITIES = ["240p", "360p", "480p", "720p", "1080p"]
OPTIMAL_QUALITIES_NO_P = ["240", "360", "480", "720", "1080"]

def sanitize_filename(filename):
    """Fayl nomini noto‘g‘ri belgilardan tozalaydi"""
    return re.sub(r'[<>:"/\\|?*\n]+', '', filename)
