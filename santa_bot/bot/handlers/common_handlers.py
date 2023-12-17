import os

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from santa_bot.bot.keyboards import (clients_start_kb, create_inline_kb,
                                     start_info_kb)
from santa_bot.bot.LEXICON import LEXICON
from santa_bot.models import Player

os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'True'

router = Router()


@router.message(Command('restart'))
@router.message(CommandStart())
async def start_command(message: Message):
    await message.answer(text=LEXICON['greeting'],
                         reply_markup=create_inline_kb())


@router.callback_query(F.data == LEXICON['ready'])
async def get_ready(callback: CallbackQuery):
    await callback.message.answer(text=LEXICON['lets_start'],
                                  reply_markup=start_info_kb())
    await callback.answer()


@router.callback_query(F.data == LEXICON['start_info'])
async def get_ready(callback: CallbackQuery):
    await callback.message.answer(text=LEXICON['group_creation_rules'],
                                  reply_markup=clients_start_kb)
    await callback.answer()


@router.message(F.text == LEXICON['my_groups'])
async def show_my_groups(message: Message):
    player_tg_id = message.chat.id
    try:
        players = Player.objects.select_related('game')  \
                                .filter(telegram_id=player_tg_id)
    except Player.DoesNotExist:
        await message.answer(LEXICON['no_groups'])
    if players:
        kb_builder = InlineKeyboardBuilder()
        buttons = [InlineKeyboardButton(text=player.game.name,
                                        callback_data=player.game.name)
                   for player in players]
        kb_builder.row(*buttons, width=1)
        await message.answer(
            text=LEXICON['player_groups'],
            reply_markup=kb_builder.as_markup(resize_keyboard=True))
    else:
        await message.answer(LEXICON['no_groups'])



# async def display_group_details(callback: CallbackQuery):
#    pass