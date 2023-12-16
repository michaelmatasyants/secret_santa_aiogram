import asyncio

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from santa_bot.bot.keyboards import clients_start_kb, create_inline_kb, start_info_kb
from santa_bot.bot.LEXICON import *

router = Router()


@router.message(CommandStart())
async def start_command(message: Message):
    text_message = "Привет, я бот-повелитель Тайных Сант. Больше всего на свете я люблю друзей и подарки 🎁"
    await message.answer(text=text_message, reply_markup=create_inline_kb())


@router.message(Command('restart'))
async def start_command(message: Message):
    text_message = "Привет, я бот-повелитель Тайных Сант. Больше всего на свете я люблю друзей и подарки 🎁"
    await message.answer(text=text_message, reply_markup=create_inline_kb())

@router.callback_query(F.data == LEXICON['ready'])
async def get_ready(callback: CallbackQuery):
    text_message = "С моей помощью ты можешь создать группу и организовать Тайного Санту с друзьями или семьей " \
                   "👨‍👩‍👧‍👦, на работе 👩‍✈️или в сообществе 🧘, везде, где есть дорогие тебе люди, " \
                   "с кем ты хочешь разделить радость новогодней суеты.\n\nВозглавь новогоднее безумие и стань душой " \
                   "этого праздника ✨"
    await callback.message.answer(text=text_message, reply_markup=start_info_kb())
    await callback.answer()


@router.callback_query(F.data == LEXICON['start_info'])
async def get_ready(callback: CallbackQuery):
    text_message = "Пока все будут собираться в твоей группе и думать, что они хотят получить от своего Санты, " \
                   "уже зарегистрированные смогут поиграть в снежки ☄️ (команда для этого будет в меню [Мои группы]) " \
                   "и порадоваться моим шуткам.\n\nКогда все соберутся, ты сможешь запустить Распределение подарков и " \
                   "я подберу и разошлю каждому его подопечного 🥷\n\nСанта и подопечный даже смогут анонимно " \
                   "пообщаться, если они захотят уточнить детали или передать привет друг другу."
    await callback.message.answer(text=text_message, reply_markup=clients_start_kb)
    await callback.answer()