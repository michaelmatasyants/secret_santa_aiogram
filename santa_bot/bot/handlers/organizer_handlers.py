import asyncio

from aiogram import Router, F
from aiogram.filters import StateFilter, CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from santa_bot.bot.keyboards import price_kb
from santa_bot.bot.LEXICON import *

storage = MemoryStorage()
router = Router()


class FSMFillForm(StatesGroup):
    name_group = State()
    description_group = State()
    choose_date = State()
    choose_price = State()
    get_link = State()


# выход из машины состояний
@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text='Отменять нечего. Вы вне машины состояний\n\n'
    )
    await message.answer(text="Нажми /start для начала работы")


@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Вы вышли из машины состояний\n\n'
    )
    await state.clear()
    await message.answer(text="Нажми /start для начала работы")


# Ветка создания групп
@router.message(Command(commands=['newgroup']), StateFilter(default_state))
async def get_ready(message: Message, state: FSMContext):
    text_message = "Самое время создать новую группу, куда ты можешь пригласить своих друзей, коллег или " \
                   "родственников\n\n" \
                   "Давай выберем забавное имя для новой группы!"
    await message.answer(text=text_message)
    await state.set_state(FSMFillForm.name_group)


@router.message(F.text == LEXICON['create_group'], StateFilter(default_state))
async def get_ready(message: Message, state: FSMContext):
    text_message = "Самое время создать новую группу, куда ты можешь пригласить своих друзей, коллег или " \
                   "родственников\n\n" \
                   "Давай выберем забавное имя для новой группы!"
    await message.answer(text=text_message)
    await state.set_state(FSMFillForm.name_group)


@router.message(StateFilter(FSMFillForm.name_group))
async def get_description_group(message: Message, state: FSMContext):
    await state.update_data(group_name=message.text)
    message_text = "Классное название!\n\n" \
                   "А теперь напиши мне короткое  описание вашей группы. Его будут видеть участники при регистрации и на странице группы."
    await message.answer(text=message_text)
    await state.set_state(FSMFillForm.description_group)


@router.message(StateFilter(FSMFillForm.description_group))
async def get_date(message: Message, state: FSMContext):
    await state.update_data(description_group=message.text)
    message_text = "Теперь все понятно!\n\n" \
                   "Пора указать дату и время проведения розыгрыша, чтобы бот уведомил участников."
    await message.answer(message_text)
    await state.set_state(FSMFillForm.choose_date)


@router.message(StateFilter(FSMFillForm.choose_date))
async def get_date(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    message_text = "Выбери стоимость подарка"

    await message.answer(message_text, reply_markup=price_kb())
    await state.set_state(FSMFillForm.get_link)


@router.message(StateFilter(FSMFillForm.choose_date))
async def get_link(message: Message, state: FSMContext):
    pass
    # await state.clear() #выход из состояний


# Ветка управления группами
@router.message(F.text == LEXICON['admin_groups'])
async def admin_group_info(message: Message):
    pass

    # text_message = "Вы админ в следующих группах:"
    # await  message.answer(text=text_message, reply_markup= # ДОПИШИ ФУНКЦИЮ)
