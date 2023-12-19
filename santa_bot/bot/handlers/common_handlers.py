import asyncio
import os

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from santa_bot.bot.keyboards import (clients_start_kb, create_inline_kb,
                                     start_info_kb)
from santa_bot.bot.LEXICON import LEXICON
from santa_bot.models import Game, Player

os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'True'

router = Router()


class FSMMyGroupsForm(StatesGroup):
    show_groups = State()
    choose_group = State()
    edit_wishlist = State()
    leave_group = State()


async def exit_fsm(handled: Message | CallbackQuery,
                   state: FSMContext):
    if isinstance(handled, Message):
        await handled.answer(text=LEXICON['exit_fsm'])
    else:
        await handled.message.answer(text=LEXICON['exit_fsm'])
    await state.clear()


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


@router.message(F.text == LEXICON['my_groups'], StateFilter(default_state))
async def show_my_groups(message: Message, state: FSMContext):
    player_tg_id = message.chat.id
    try:
        players = Player.objects.select_related('game')  \
                                .filter(telegram_id=player_tg_id)
    except Player.DoesNotExist:
        await message.answer(LEXICON['no_groups'])
        await exit_fsm(message, state)
    if players:
        kb_builder = InlineKeyboardBuilder()
        buttons = [InlineKeyboardButton(text=player.game.name,
                                        callback_data=player.game.name)
                   for player in players]
        kb_builder.row(*buttons, width=1)
        await message.answer(
            text=LEXICON['all_player_groups'],
            reply_markup=kb_builder.as_markup(resize_keyboard=True))
        await state.set_state(FSMMyGroupsForm.show_groups)
    else:
        await message.answer(LEXICON['no_groups'])
        await exit_fsm(message, state)


@router.callback_query(StateFilter(FSMMyGroupsForm.show_groups))
async def display_group_details(callback: CallbackQuery,
                                state: FSMContext):
    await state.update_data(game_name=callback.data)
    game = Game.objects.get(name=callback.data)
    players = '\n'.join([player.name for player
                         in game.players.all().iterator()])
    players_wishlist = Player.objects.get(telegram_id=callback.from_user.id,
                                          game=game).wishlist
    txt_message = LEXICON['group_info'].format(
            game.name,
            game.description,
            'закрыта' if game.players_distributed else 'открыта',
            game.price_limit,
            players_wishlist,
            players,
            'Передать после распределения подарков через if')
    keyboard = [
        [InlineKeyboardButton(text=btn, callback_data=btn)]
        for btn in LEXICON['group_info_btns'].split(', ')
    ]
    await callback.message.answer(
            text=txt_message,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()
    await state.set_state(FSMMyGroupsForm.choose_group)


@router.callback_query(StateFilter(FSMMyGroupsForm.choose_group))
async def group_actions(callback: CallbackQuery,
                        state: FSMContext):
    back, edit, leave = LEXICON['group_info_btns'].split(', ')
    if callback.data == back:
        await exit_fsm(callback, state)
    elif callback.data == edit:
        await callback.message.answer(text=LEXICON['change_wishlist'])
        await state.set_state(FSMMyGroupsForm.edit_wishlist)
    elif callback.data == leave:
        kb = [
            [
                InlineKeyboardButton(text=LEXICON['yes'],
                                     callback_data=LEXICON['yes'])
            ],
            [InlineKeyboardButton(text=LEXICON['no'],
                                  callback_data=LEXICON['no'])]
        ]
        await callback.message.answer(
            text=LEXICON['wanna_leave_group'],
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
        await state.set_state(FSMMyGroupsForm.leave_group)


@router.message(StateFilter(FSMMyGroupsForm.edit_wishlist))
async def change_wishlist(message: Message, state: FSMContext):
    answer = await state.get_data()
    player = Player.objects.select_related('game')  \
                   .filter(telegram_id=message.chat.id,
                           game__name=answer['game_name'])[0]
    player.wishlist = message.text
    player.save()

    txt_message = LEXICON['wishlist_is_changed'].format(message.text)
    await message.answer(text=txt_message)
    await asyncio.sleep(1)
    await exit_fsm(message, state)


@router.callback_query(StateFilter(FSMMyGroupsForm.leave_group))
async def leave_group(callback: CallbackQuery, state: FSMContext):
    if callback.data == LEXICON['no']:
        await exit_fsm(callback, state)
    elif callback.data == LEXICON['yes']:
        answer = await state.get_data()
        player = Player.objects.select_related('game')  \
                       .filter(telegram_id=callback.from_user.id,
                               game__name=answer['game_name'])

        player.delete()
        txt_message = LEXICON['successfully_exited'].format(
                                                        answer['game_name'])
        await callback.message.answer(text=txt_message)
        await asyncio.sleep(1)
        await exit_fsm(callback, state)
