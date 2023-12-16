from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from santa_bot.bot.LEXICON import *

clients_start_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=LEXICON['create_group'])],
              [KeyboardButton(text=LEXICON['my_groups'])],
              [KeyboardButton(text=LEXICON['admin_groups'])],
              ],
    resize_keyboard=True)


def create_inline_kb():
    ready_inline_kb = InlineKeyboardButton(text=LEXICON['ready'], callback_data=LEXICON['ready'])
    create_inline = InlineKeyboardMarkup(inline_keyboard=[[ready_inline_kb]])

    return create_inline


def start_info_kb():
    start_kb = InlineKeyboardButton(text=LEXICON['start_info'], callback_data=LEXICON['start_info'])
    create_inline = InlineKeyboardMarkup(inline_keyboard=[[start_kb]])

    return create_inline
