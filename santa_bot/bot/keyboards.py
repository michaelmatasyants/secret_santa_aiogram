from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)

from santa_bot.bot.LEXICON import LEXICON

clients_start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=LEXICON['create_group'])],
        [KeyboardButton(text=LEXICON['my_groups'])],
        [KeyboardButton(text=LEXICON['admin_groups'])],
    ],
    resize_keyboard=True)


def create_inline_kb():
    """Create ready inline keyboard"""
    ready_inline_kb = InlineKeyboardButton(text=LEXICON['ready'],
                                           callback_data=LEXICON['ready'])
    create_inline = InlineKeyboardMarkup(inline_keyboard=[[ready_inline_kb]])
    return create_inline


def start_info_kb():
    """Create start keyboard"""
    start_kb = InlineKeyboardButton(text=LEXICON['start_info'],
                                    callback_data=LEXICON['start_info'])
    create_inline = InlineKeyboardMarkup(inline_keyboard=[[start_kb]])
    return create_inline


def price_kb():
    """Create price keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text=LEXICON['price_1'],
                                 callback_data="price#1")
        ],
        [
            InlineKeyboardButton(text=LEXICON['price_2'],
                                 callback_data="price#2")
        ],
        [
            InlineKeyboardButton(text=LEXICON['price_3'],
                                 callback_data="price#3")
        ],
    ]
    price_keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return price_keyboard


def confirm_bt():
    keyboard = [
        [
            InlineKeyboardButton(text=LEXICON['ok'],
                                 callback_data=LEXICON['ok'])
        ],
        [
            InlineKeyboardButton(text=LEXICON['mistake'],
                                 callback_data='user_rename')
        ],
    ]
    create_confirm_kb = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return create_confirm_kb


def corrections_bt():
    keyboard = [
        [
            InlineKeyboardButton(text='Внести изменения',
                                 callback_data='user_rename')
        ],
    ]
    create_corrections_kb = InlineKeyboardMarkup(inline_keyboard=keyboard)

    return create_corrections_kb
