import os

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async

from santa_bot.bot.LEXICON import LEXICON
from santa_bot.models import Organizer, Player

os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'True'

router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    await message.answer(text='это старт')



@router.message(F.text == LEXICON['my_groups'])
async def show_my_groups(message: Message):
    player_tg_id = message.chat.id
    try:
        players = Player.objects.select_related('game').filter(telegram_id=player_tg_id)
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
