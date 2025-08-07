import asyncio

import yt_dlp
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputFile, FSInputFile

from config import DB_NAME, ADMINS
from handlers.state.user_state import UserState
from handlers.state.user_state import Youtube, Instagram
from keybords.helper import sanitize_filename
from keybords.inleniekeybor import lang_sort, get_best_quality_keyboard, get_best_quality_keyboard_inst
from utils.database import Database
import imageio_ffmpeg as ffmpeg
import os

cmd_router = Router()
db = Database(DB_NAME)


# Guruhdagi barcha matnli xabarlarni o'qish
# @cmd_router.message(F.chat.type.in_({'group', 'supergroup'}))  # Guruh yoki superguruhdan xabarlar
# async def read_group_messages(message: Message):
#     await message.bot.send_message(text=message.text, chat_id=ADMINS[0])


# ------------------------- YOUTUBE --------------------------------
@cmd_router.message(F.text.startswith("https://youtu"))
async def youtube_download(message: Message, state: FSMContext):
    await state.update_data(url=message.text)
    url = message.text
    keyboard = await get_best_quality_keyboard(url)

    if keyboard:
        await state.set_state(Youtube.quality_choice)
        await message.answer("Quyidagi sifatlardan birini tanlang:", reply_markup=keyboard)
    else:
        await message.answer("🔴 Videoning sifati topilmadi yoki yuklab bo‘lmaydi.")


@cmd_router.callback_query(Youtube.quality_choice)
async def process_quality_choice(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.message.delete()
    format_id = callback_query.data.replace("download_", "")
    url = await state.get_data()
    url = url.get('url')

    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    is_audio = format_id == "mp3"

    ydl_opts = {
        'format': f'{format_id}+bestaudio/best' if not is_audio else 'bestaudio',
        'merge_output_format': 'mp4' if not is_audio else 'mp3',
        'outtmpl': f'{output_dir}/{callback_query.from_user.id}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if is_audio else []
    }

    msg = await callback_query.message.answer("⏳ Yuklanmoqda, biroz kuting...")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    file_ext = "mp3" if is_audio else "mp4"
    file_path = os.path.join(output_dir, f"{callback_query.from_user.id}.{file_ext}")

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        media_file = FSInputFile(file_path)
        file_size = round(os.path.getsize(file_path) / 1048576, 2)  # MB ga o'tkazish
        if is_audio:
            await bot.send_audio(chat_id=callback_query.from_user.id, audio=media_file, caption=f"MP3 hajmi: {file_size} MB")
        else:
            await bot.send_video(chat_id=callback_query.from_user.id, video=media_file, caption=f"Video hajmi: {file_size} MB")
        await callback_query.message.answer("✅ Yuklab olindi va yuborildi!")
        os.remove(file_path)
    else:
        await callback_query.message.answer("❌ Yuklab olishda xatolik yuz berdi!")

    await state.clear()


# ------------------------------ instagram ------------------------------
@cmd_router.message(F.text.startswith("https://www.instagram.com"))
async def instagram_download(message: Message, state: FSMContext):
    await state.update_data(url=message.text)
    url = message.text
    keyboard = await get_best_quality_keyboard_inst(url)

    if keyboard:
        await state.set_state(Instagram.quality_choice)
        await message.answer("Quyidagi sifatlardan birini tanlang:", reply_markup=keyboard)
    else:
        await message.answer("🔴 Videoning sifati topilmadi yoki yuklab bo‘lmaydi.")


@cmd_router.callback_query(Instagram.quality_choice)
async def process_quality_choice(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.message.delete()
    format_id = callback_query.data.replace("download_", "")
    url = await state.get_data()
    url = url.get('url')

    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    is_audio = format_id == "mp3"

    ydl_opts = {
        'format': f'{format_id}+bestaudio/best' if not is_audio else 'bestaudio',
        'merge_output_format': 'mp4' if not is_audio else 'mp3',
        'outtmpl': f'{output_dir}/{callback_query.from_user.id}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if is_audio else []
    }

    msg = await callback_query.message.answer("⏳ Yuklanmoqda, biroz kuting...")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    file_ext = "mp3" if is_audio else "mp4"
    file_path = os.path.join(output_dir, f"{callback_query.from_user.id}.{file_ext}")

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        media_file = FSInputFile(file_path)
        file_size = round(os.path.getsize(file_path) / 1048576, 2)
        if is_audio:
            await bot.send_audio(chat_id=callback_query.from_user.id, audio=media_file, caption=f"MP3 hajmi: {file_size} MB")
        else:
            await bot.send_video(chat_id=callback_query.from_user.id, video=media_file, caption=f"Video hajmi: {file_size} MB")
        await callback_query.message.answer("✅ Yuklab olindi va yuborildi!")
        os.remove(file_path)
    else:
        await callback_query.message.answer("❌ Yuklab olishda xatolik yuz berdi!")

    await state.clear()


# --------------------------------- REF ----------------------------
@cmd_router.message(Command('ref'))
async def ref(message: Message, state: FSMContext):
    await message.bot.send_message(text=f'https://t.me/math_hard_bot?start={message.from_user.id}', chat_id=message.from_user.id)


@cmd_router.message(Command('start'))
async def start(message: Message, state: FSMContext):
    await message.bot.send_message(text='Assalomu aleykum, botimizga xush kelibsiz!', chat_id=message.from_user.id)

# @cmd_router.message(Command('hamster'))
# async def tanalsh_func(message: Message, state: FSMContext):
#     url = r'https://digitalninja.ru/hamster'   # Send a GET request to the URL
#
#     response = requests.get(url)
#
#     # Parse HTML content
#     soup = BeautifulSoup(response.content, 'html.parser')
#     # print(soup)
#     divs = soup.find_all('div', class_='promo-item__name')
#     div_texts = [div.get_text(strip=True) for div in divs]
#     await message.answer(text='Tanlang:', reply_markup=hamster_inline_keyboard(div_texts))
#     await state.set_state(HamsterState.tanalsh)
#     # ChromeDriver yo'lini ko'rsating
#
#
# @cmd_router.callback_query(HamsterState.tanalsh)
# async def hamster_loading(cb_query: CallbackQuery, state: FSMContext):
#     await cb_query.message.delete()
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")  # Brauzerni ko'rinmasdan ishga tushirish
#     chrome_options.add_argument("--no-sandbox")  # Bu ba'zi hostinglarda kerak bo'lishi mumkin
#     chrome_options.add_argument("--disable-dev-shm-usage")  # Tizim xotira muammolaridan qochish uchun
#
#     # Driver boshqaruvi
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
#
#     # Sahifani ochish
#     driver.get('https://digitalninja.ru/hamster')
#
#     # Tugmani bosishdan oldin holatni olish
#     await asyncio.sleep(3)  # 3 soniya kutish (sahifa yuklanishi uchun)
#
#     # Ma'lumotlarni olish
#     buttons = driver.find_elements(By.CLASS_NAME, 'promo-item.content-wrapper')
#     for number, item in enumerate(buttons):
#         if number == int(cb_query.data):
#             item.click()
#
#     # Tugmani bosgandan keyin kutish va yana bosish
#     for _ in range(3):
#         warning_buttons = driver.find_elements(By.CLASS_NAME, 'btn.btn_warning')
#         for warning_button in warning_buttons:
#             warning_button.click()
#             await asyncio.sleep(1)
#
#     # Tugmani bosgandan keyin sahifa o'zgarishi uchun kutish
#     buttons_foiz = driver.find_elements(By.CLASS_NAME, 'result-loading__label')
#     holat = True
#     zxc = 0
#     while holat:
#         zxc += 1
#         try:
#             for button_foiz in buttons_foiz:
#                 if button_foiz.text == '':
#                     holat = False
#                 await asyncio.sleep(5)
#             print(cb_query.from_user.first_name, zxc)
#         except:
#             holat = False
#     # Promo kodlarni olish
#     await asyncio.sleep(5)
#     promo_cods = driver.find_elements(By.CLASS_NAME, 'promo-code__text')
#     for promo_cod in promo_cods:
#         await cb_query.bot.send_message(
#             text=f"<code>{promo_cod.text}</code>",
#             chat_id=cb_query.from_user.id,
#             parse_mode="HTML"
#         )
#
#     # Brauzerni yopish
#     driver.quit()

    # url = (r'https://digitalninja.ru/hamster')    # Send a GET request to the URL
    #
    # response = requests.get(url)
    #
    # # Parse HTML content
    # soup = BeautifulSoup(response.content, 'html.parser')
    # # print(soup)
    # button = soup.find_all('button', class_='promo-item content-wrapper')

    # await message.answer(text=f"https://t.me/math_hard_bot?start={message.from_user.id}") # referal
#
# @cmd_router.callback_query(Test.Game)
# async def get_category(cb_query: CallbackQuery, state: FSMContext):
#     await state.update_data(region=cb_query.data)
#     if cb_query.data == '1':
#         await cb_query.bot.edit_message_text(
#             text='Toifani belgilang', chat_id=cb_query.from_user.id, message_id=cb_query.message.message_id,
#             reply_markup=get_category_markup())
#     else:
#         await cb_query.bot.edit_message_text(
#             text='Toifani belgilang', chat_id=cb_query.from_user.id, message_id=cb_query.message.message_id,
#             reply_markup=get_category_markup2())
#     await state.set_state(Test.Game1)
#
#
# @cmd_router.callback_query(Test.Game1)
# async def handle_callback_query(cb_query: CallbackQuery, state: FSMContext):
#     if cb_query.data == 'back':
#         await cb_query.bot.edit_message_text(
#             text="O'zinggizga kerak viloyatni tanlang",
#             chat_id=cb_query.from_user.id,
#             message_id=cb_query.message.message_id,
#             reply_markup=get_region_list())
#         await state.set_state(Test.Game)
#     else:
#         await state.update_data(toifa=cb_query.data)
#         await cb_query.bot.edit_message_text(
#             text='qancha kun ?',
#             chat_id=cb_query.from_user.id,
#             message_id=cb_query.message.message_id,
#             reply_markup=days_markup()
#         )
#         await state.set_state(Test.Game2)
#
#
# @cmd_router.callback_query(Test.Game2)
# async def send_message(cb_query: CallbackQuery, state: FSMContext):
#     if cb_query.data == 'back':
#         await cb_query.bot.edit_message_text(
#             text='Toifani belgilang', chat_id=cb_query.from_user.id, message_id=cb_query.message.message_id,
#             reply_markup=get_category_markup() if int(
#                 (await state.get_data())['region']) == 1 else get_category_markup2())
#         await state.set_state(Test.Game1)
#     else:
#         # ---------------DATA------------
#         all_data = await state.get_data()
#         reg_id = int(all_data['region'])
#         toifa = all_data['toifa']
#         days = int(cb_query.data)
#         # --------------- DATE ---------------
#         sana = datetime.now() + timedelta(days=days)
#         sana_str = sana.strftime('%d-%m-%Y')
#         # ------------------------------------
#         price_list = price_shahar if reg_id == 1 else price_viloyat
#         reg_type = toshkent if reg_id == 1 else others
#         toifa_narxi = price_list[price_list.index(int(toifa))]
#
#         await state.clear()
#         await cb_query.message.delete()
#         text = (f"<b>Бугун: {sana_str}</b>  \n\n"
#                 f"💸:<b>{reg_type[toifa_narxi]['crl']} \n\n Худуд: {regions[reg_id - 1]}</b>\n\n")
#         all_data = db.get_numbers_reg_price(reg_id, toifa)
#         len_data = sikl_data(len(all_data))
#         qwerty = len_data
#         for i, number in enumerate(all_data):
#             if i % 2 == 1:
#                 text += f"  <b>{reg_type[toifa_narxi]['sticker']}  {number[5]}</b>\n"
#             else:
#                 text += f"<b>{number[5]}</b>"
#             if i == len_data:
#                 len_data += qwerty
#                 await cb_query.bot.send_message(text=text, chat_id=cb_query.from_user.id)
#                 text = (f"<b>Бугун: {sana_str}</b>  \n\n"
#                         f"💸:<b>{reg_type[toifa_narxi]['crl']} \n\n Худуд: {regions[reg_id - 1]}</b>\n\n")
#         if len(all_data) % qwerty != 0:
#             await cb_query.bot.send_message(text=text, chat_id=cb_query.from_user.id)
#
#
#
#
# @cmd_router.message()
# async def test_1(message: Message):
#     for i in message:
#         print(i)
#     region_id = message.text[0:2]
#     number = message.text[3:11]
#     data = db.search_number(region_id, number)
#     if data:
#         await message.answer(text=f"{regions[int(data[1]) - 1]}\n"
#                                   f"<a href='https://avtoraqam.uzex.uz/ru/lot/item/{data[2]}'>lot number</a>: {data[2]}\n"
#                                   f"{data[3]}\n"
#                                   f"{data[4]} {data[5]}\n"
#                                   f"{data[6]} so'm\n"
#                                   f"{data[7]} {data[8]}")
#     else:
#         await message.answer(text=f"'{message.text}' Bunday nomer topilmadi iltimos nomer shunaqa xolatda "
#                                   f"bo'lsin\nNamuna:01 A 001 AA")
