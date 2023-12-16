import asyncio

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from santa_bot.bot.keyboards import clients_start_kb, create_inline_kb
from santa_bot.bot.LEXICON import *

router = Router()


# @router.message(Command('restart'))
# async def start_command(message: Message):
#     text_message = "Привет, я бот-повелитель Тайных Сант. Больше всего на свете я люблю друзей и подарки 🎁"
#     await message.answer(text=text_message, reply_markup=create_inline_kb())

# Ветка создания групп
@router.message(F.text == LEXICON['create_group'])
async def get_ready(message: Message):
    text_message = "Самое время создать новую группу, куда ты можешь пригласить своих друзей, коллег или " \
                   "родственников\n\n" \
                   "Давай выберем забавное имя для новой группы!"
    await message.answer(text=text_message)

# Ветка управления группами
@router.message(F.text == LEXICON['admin_groups'])
async def admin_group_info(message: Message):
    text_message = "Вы админ в следующих группах:"
    await  message.answer(text=text_message, reply_markup= # ДОПИШИ ФУНКЦИЮ)
