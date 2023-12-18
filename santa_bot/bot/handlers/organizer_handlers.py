from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.markdown import link
from aiogram import Bot
from django.conf import settings

from santa_bot.models import Game

from pathlib import Path
from santa_bot.bot.keyboards import price_kb, get_group_kb
from santa_bot.bot.LEXICON import LEXICON

storage = MemoryStorage()
router = Router()
bot = Bot(settings.TELEGRAM_TOKEN)


class FSMFillForm(StatesGroup):
    name_group = State()
    description_group = State()
    game_date = State()
    choose_date = State()
    choose_price = State()
    get_link = State()


class FSMAdminForm(StatesGroup):
    group_information = State()
    group_confirm = State()
    send_wishlist = State()


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
@router.message(F.text == LEXICON['create_group'], StateFilter(default_state))
async def get_ready(message: Message, state: FSMContext):
    text_message = "Самое время создать новую группу, куда ты можешь пригласить своих друзей, коллег или " \
                   "родственников\n\n" \
                   "Давай выберем забавное имя для новой группы!"
    await message.answer(text=text_message)
    await state.set_state(FSMFillForm.name_group)


@router.message(StateFilter(FSMFillForm.name_group))
async def get_description_group(message: Message, state: FSMContext):
    await state.update_data(name_group=message.text)
    message_text = "Классное название!\n\n" \
                   "А теперь напиши мне короткое описание вашей группы. Его будут видеть участники при регистрации и на странице группы."
    await message.answer(text=message_text)
    await state.set_state(FSMFillForm.description_group)


@router.message(StateFilter(FSMFillForm.description_group))
async def get_game_date(message: Message, state: FSMContext):
    await state.update_data(description_group=message.text)
    message_text = "А когда все узнают своих подопечных?\n\n" \
                   "Пора указать дату."
    await message.answer(message_text)
    await state.set_state(FSMFillForm.game_date)


@router.message(StateFilter(FSMFillForm.game_date))
async def get_date(message: Message, state: FSMContext):
    await state.update_data(game_date=message.text)
    message_text = "Теперь все понятно!\n\n" \
                   "Пора указать дату и время проведения розыгрыша, чтобы бот уведомил участников."
    await message.answer(message_text)
    await state.set_state(FSMFillForm.choose_date)


@router.message(StateFilter(FSMFillForm.choose_date))
async def get_price(message: Message, state: FSMContext):
    await state.update_data(choose_date=message.text)
    message_text = "Выбери стоимость подарка"

    await message.answer(message_text, reply_markup=price_kb())
    await state.set_state(FSMFillForm.get_link)


@router.callback_query(StateFilter(FSMFillForm.get_link), F.data.in_(['price_1', 'price_2', 'price_3']))
async def get_link(callback: CallbackQuery, state: FSMContext):
    await state.update_data(choose_price=LEXICON[callback.data])
    link = await create_start_link(bot=bot, payload='123')
    await state.update_data(get_link=link)
    await callback.message.answer(text=f"{LEXICON['link']}\n\n{link}")
    await callback.answer()
    await state.clear()
    #print(link)
    # await state.clear() #выход из состояний


# Ветка управления группами
@router.message(F.text == LEXICON['admin_groups'], StateFilter(default_state))
async def admin_group_info(message: Message, state: FSMContext):  # ДОБАВИТЬ ГРУППЫ ИЗ БД
    groups = Game.objects.filter(organizer__telegram_id=message.from_user.id)
    print(groups)
    text_message = LEXICON['your_groups']
    await message.answer(text=text_message, reply_markup=get_group_kb(groups))
    await state.set_state(FSMAdminForm.group_information)


@router.callback_query(StateFilter(FSMAdminForm.group_information), F.data.in_(['your_groups', ]))
async def start_user(callback: CallbackQuery, state: FSMContext):
    print(callback.message.text)
    await state.update_data(group_information=callback.message.text)
    group_info = {
        "name": callback.message.text,
        "description": "Куча текста",
        "registration_status": "Открыта",
        "amount_playing_users": 6,
    }
    text = "Название группы: {}\n\n" \
           "Описание:\n{}\n\n" \
           "Регистрация в группу {}\n\n" \
           "Количество участников (через annotate) - {}\n"

    message_text = text.format(group_info['name'],
                               group_info["description"],
                               group_info['registration_status'],
                               group_info['amount_playing_users'],
                               )
    await callback.message.answer(text=message_text)
    await state.set_state(FSMAdminForm.group_confirm)
