import asyncio

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message

from santa_bot.bot.handlers.common_handlers import exit_fsm
from santa_bot.bot.keyboards import confirm_bt
from santa_bot.bot.LEXICON import LEXICON
from santa_bot.models import Game, Player

storage = MemoryStorage()
router = Router()


class FSMUserForm(StatesGroup):
    user_name = State()
    email = State()
    wishlist = State()
    check_data = State()
    data_change = State()
    game = State()


@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text='Отменять нечего. Вы вне машины состояний\n\n'
    )
    await message.answer(text="Нажми /start для начала работы")


@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    # if message.text in LEXICON['kb_buttons']:
    #     await exit_fsm()
    await message.answer(
        text='Вы вышли из машины состояний\n\n'
    )
    await state.clear()
    await message.answer(text="Нажми /start для начала работы")


@router.callback_query(StateFilter(FSMUserForm.check_data), F.data.in_(['data_change']))
async def editing_start_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text=LEXICON['user_name'])
    await callback.answer()
    await state.set_state(FSMUserForm.user_name)


# @router.message(Command(commands=['start']), StateFilter(default_state))
# async def start_user(message: Message, state: FSMContext):
#
#     game_id = int(message.text.split(" ")[-1])
#     try:
#         game = Game.objects.get(id=game_id)
#     except Game.DoesNotExist:
#         await message.answer("Данная игра уже недоступна!")
#     await state.update_data(game=game)
#     if Player.objects.filter(telegram_id=message.from_user.id,game=game)  \
#                      .exists():
#         await message.answer("Вы уже зарегистрированы на эту игру")
#         return
#
#     text_message = LEXICON['game'].format(
#                          game.name,
#                          game.start_date,
#                          game.end_date,
#                          game.description)
#     await message.answer(text=text_message)
#     await asyncio.sleep(0.5)
#     await message.answer(text=LEXICON['user_name'])
#     await state.set_state(FSMUserForm.user_name)


@router.message(StateFilter(FSMUserForm.user_name))
async def get_email(message: Message, state: FSMContext):
    # if message.text in LEXICON['kb_buttons']:
    #     await exit_fsm(message, state)
    await state.update_data(user_name=message.text)
    message_text = LEXICON['email']
    await message.answer(text=message_text)
    await state.set_state(FSMUserForm.email)


@router.message(StateFilter(FSMUserForm.email))
async def get_wishlist(message: Message, state: FSMContext):
    # if message.text in LEXICON['kb_buttons']:
    #     await exit_fsm(message, state)
    await state.update_data(email=message.text)
    message_text = LEXICON['wishlist']
    await message.answer(text=message_text)
    await state.set_state(FSMUserForm.wishlist)


@router.message(StateFilter(FSMUserForm.wishlist))
async def get_check(message: Message, state: FSMContext):
    # if message.text in LEXICON['kb_buttons']:
    #     await exit_fsm(message, state)
    await state.update_data(wishlist=message.text)
    answer = await state.get_data()
    message_text = LEXICON['check_data'].format(
        answer['user_name'],
        answer['email'],
        answer['wishlist'])
    await message.answer(text=message_text, reply_markup=confirm_bt())

    await state.set_state(FSMUserForm.check_data)


@router.callback_query(StateFilter(FSMUserForm.check_data),
                       F.data.in_(['data_save']))
async def get_decision(callback: CallbackQuery, state: FSMContext):
    answer = await state.get_data()
    game = answer['game']
    participation = Player.objects.create(
        telegram_id=callback.from_user.id,
        game=game,
        name=answer['user_name'],
        email=answer['email'],
        wishlist=answer['wishlist']
    )
    message_text = LEXICON['in_game'].format(game.end_date)
    await callback.message.answer(text=message_text)
    await callback.answer()
    await state.clear()
