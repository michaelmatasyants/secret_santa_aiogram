import os
from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile
from django.conf import settings

bot = Bot(settings.TELEGRAM_TOKEN)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


async def message_send_photo(message, image):
    file_path = os.path.join(BASE_DIR / "media", f'{image}')
    default_file_path = os.path.join(BASE_DIR / "static/bot_img", f'{image}')
    if os.path.isfile(file_path):
        photo = FSInputFile(path=file_path, filename=f'{image}')
        await bot.send_photo(chat_id=message.chat.id, photo=photo)
    else:
        photo = FSInputFile(path=default_file_path, filename=f'{image}')
        await bot.send_photo(chat_id=message.chat.id, photo=photo)


async def callback_send_photo(callback, image):
    file_path = os.path.join(BASE_DIR / "media", f'{image}')
    default_file_path = os.path.join(BASE_DIR / "static/bot_img", f'{image}')
    if os.path.isfile(file_path):
        photo = FSInputFile(path=file_path, filename=f'{image}')
        await callback.message.answer_photo(photo=photo)
    else:
        photo = FSInputFile(path=default_file_path, filename=f'{image}')
        await callback.message.answer_photo(photo=photo)
