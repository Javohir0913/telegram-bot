import yt_dlp
from .helper import tillar, OPTIMAL_QUALITIES
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def get_best_quality_keyboard(url):
    ydl_opts = {'quiet': True}
    best_qualities = {}
    mp3_size = None

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        for format in info.get('formats', []):
            format_note = format.get('format_note')
            filesize = format.get('filesize') or 0  # None bo‘lsa, 0 qiymatini beramiz
            format_id = format.get('format_id')

            if format_note in OPTIMAL_QUALITIES:
                old_size = best_qualities.get(format_note, {}).get('filesize', 0)  # None bo‘lsa, 0
                if format_note not in best_qualities or old_size < filesize:
                    best_qualities[format_note] = {'format_id': format_id, 'filesize': filesize}

        if 'bestaudio' in info and isinstance(info['bestaudio'], dict):
            mp3_size = info['bestaudio'].get('filesize') or 0  # None bo‘lsa, 0

    # Videolarni sifat bo‘yicha tartiblash
    video_buttons = sorted(
        [
            InlineKeyboardButton(
                text=f"{q} ({round(best_qualities[q]['filesize'] / 1048576, 2)} MB)",
                callback_data=f"download_{best_qualities[q]['format_id']}"
            )
            for q in best_qualities if best_qualities[q]['filesize'] > 0  # 0 MB fayllarni chiqarib tashlash
        ],
        key=lambda btn: OPTIMAL_QUALITIES.index(btn.text.split()[0])  # Sifat tartibi bo‘yicha saralash
    )

    # Har bir tugmani alohida qatorga qo‘yish
    buttons = [[btn] for btn in video_buttons]

    # MP3 tugmasini oxiriga qo‘shish
    mp3_size = info.get('bestaudio', {}).get('filesize', 0) or 0  # Agar None bo‘lsa, 0

    if mp3_size > 0:
        buttons.append([
            InlineKeyboardButton(
                text=f"🎵 MP3 (Audio) ({round(mp3_size / 1048576, 2)} MB)",
                callback_data="download_mp3"
            )
        ])
    else:
        buttons.append([InlineKeyboardButton(text="🎵 MP3 (Audio)", callback_data="download_mp3")])

    return InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None


async def get_best_quality_keyboard_inst(url):
    ydl_opts = {'quiet': True}
    best_qualities = {}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        for format in info.get('formats', []):
            format_id = format.get('format_id')
            filesize = format.get('filesize') or 0
            resolution = format.get('height')
            if resolution and format_id:
                best_qualities[resolution] = {'format_id': format_id, 'filesize': filesize}
    video_buttons = sorted(
        [
            InlineKeyboardButton(
                text=f"{res}p ({round(best_qualities[res]['filesize'] / 1048576, 2)} MB)",
                callback_data=f"download_{best_qualities[res]['format_id']}"
            )
            for res in sorted(best_qualities, reverse=True)
        ],
        key=lambda btn: int(btn.text.split('p')[0]),
        reverse=True
    )

    buttons = [[btn] for btn in video_buttons]
    # MP3 tugmasini oxiriga qo‘shish
    mp3_size = info.get('bestaudio', {}).get('filesize', 0) or 0  # Agar None bo‘lsa, 0
    if mp3_size > 0:
        buttons.append([
            InlineKeyboardButton(
                text=f"🎵 MP3 (Audio) ({round(mp3_size / 1048576, 2)} MB)",
                callback_data="download_mp3"
            )
        ])
    else:
        buttons.append([InlineKeyboardButton(text="🎵 MP3 (Audio)", callback_data="download_mp3")])

    return InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None


def lang_sort() -> InlineKeyboardMarkup:
    row1 = []
    row2 = []
    for item in tillar:
        date = InlineKeyboardButton(text=item, callback_data=item)
        if item == 'UZ':
            row1.append(date)
        else:
            row2.append(date)
    rows = [row1, row2]

    markup = InlineKeyboardMarkup(inline_keyboard=rows)

    return markup


