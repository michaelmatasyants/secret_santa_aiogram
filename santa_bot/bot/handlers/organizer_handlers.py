import os
from pathlib import Path

from aiogram import Bot, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, LabeledPrice, Message,
                           PreCheckoutQuery, FSInputFile)
from aiogram.utils.deep_linking import create_start_link
from django.conf import settings
from django.db.models import Count

from santa_bot.bot.functions import message_send_photo
from santa_bot.bot.keyboards import get_group_kb, price_kb
from santa_bot.bot.LEXICON import LEXICON
from santa_bot.models import Game, Organizer


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

storage = MemoryStorage()
router = Router()
bot = Bot(settings.TELEGRAM_TOKEN)


class FSMFillForm(StatesGroup):
    group_name = State()
    group_description = State()
    game_date = State()
    choose_date = State()
    choose_price = State()
    get_link = State()


class FSMAdminForm(StatesGroup):
    group_information = State()
    group_confirm = State()
    send_wishlist = State()


class FSMPaymentForm(StatesGroup):
    payment = State()
    invoice = State()


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
    await state.clear()
    text_message = "Самое время создать новую группу, куда ты можешь пригласить своих друзей, коллег или " \
                   "родственников\n\n" \
                   "Давай выберем забавное имя для новой группы!"
    await message.answer(text=text_message)
    await state.set_state(FSMFillForm.group_name)


@router.message(StateFilter(FSMFillForm.group_name))
async def get_description_group(message: Message, state: FSMContext):
    await state.update_data(group_name=message.text)
    message_text = "Классное название!\n\n" \
                   "А теперь напиши мне короткое описание вашей группы. Его будут видеть участники при регистрации и на странице группы."
    await message.answer(text=message_text)
    await state.set_state(FSMFillForm.group_description)


@router.message(StateFilter(FSMFillForm.group_description))
async def get_game_date(message: Message, state: FSMContext):
    current_state = await state.set_state()
    await state.update_data(group_description=message.text)

    await message_send_photo(message, 'firework.jpg')
    await message.answer(text=LEXICON['santa_selection_date'])
    await state.set_state(FSMFillForm.game_date)


@router.message(StateFilter(FSMFillForm.game_date))
async def get_date(message: Message, state: FSMContext):
    await state.update_data(game_date=message.text)
    message_text = "Теперь все понятно!\n\n" \
                   "Пора указать дату и время проведения розыгрыша, "  \
                   "чтобы бот уведомил участников.\n"  \
                   "Формат ввода ГГГГ-ММ-ДД ЧЧ:ММ:СС"
    await message.answer(message_text)
    await state.set_state(FSMFillForm.choose_date)


@router.message(StateFilter(FSMFillForm.choose_date))
async def get_price(message: Message, state: FSMContext):
    # картинка подарка с бантом
    await state.update_data(choose_date=message.text)
    message_text = "Выбери стоимость подарка"
    await message_send_photo(message, 'present2.jpg')
    await message.answer(message_text, reply_markup=price_kb())
    await state.set_state(FSMFillForm.get_link)


@router.callback_query(StateFilter(FSMFillForm.get_link),
                       F.data.in_(['price_1', 'price_2', 'price_3']))
async def get_link(callback: CallbackQuery, state: FSMContext):
    await state.update_data(choose_price=LEXICON[callback.data])
    answers = await state.get_data()
    new_game = Game.objects.create(
        organizer=Organizer.objects.get_or_create(
            telegram_id=callback.from_user.id)[0],
        name=answers['group_name'],
        description=answers['group_description'],
        price_limit=answers["choose_price"],
        end_date=answers['game_date'],
        send_date=answers['choose_date'],
    )
    link = await create_start_link(bot=bot, payload=new_game.id)
    new_game.link = link
    new_game.save()
    await state.update_data(get_link=link)
    await callback.message.answer(text=f"{LEXICON['link']}\n\n{link}")
    await callback.answer()
    await state.clear()


# Ветка управления группами
@router.message(F.text == LEXICON['admin_groups'], StateFilter(default_state))
async def admin_group_info(message: Message, state: FSMContext):
    await state.clear()
    groups = Game.objects.filter(organizer__telegram_id=message.from_user.id)
    # картинка с управлением группами (менеджмент или что-то похожее)
    text_message = LEXICON['your_groups']
    await message_send_photo(message, 'anta-manager.jpg')
    await message.answer(text=text_message, reply_markup=get_group_kb(groups))
    await state.set_state(FSMAdminForm.group_information)


@router.callback_query(StateFilter(FSMAdminForm.group_information), F.data.startswith('group_id#'))
async def start_user(callback: CallbackQuery, state: FSMContext):
    group_id = callback.data.split("#")[-1]
    game = Game.objects.filter(id=group_id).annotate(player_count=Count("players"))[0]
    await state.update_data(group_information=callback.message.text)
    status = "закрыта" if game.players_distributed else "открыта"
    message_text = f"Название группы: {game.name}\n\n" \
        f"Описание:\n{game.description}\n\n" \
        f"Регистрация в группу {status}\n\n" \
        f"Количество участников: {game.player_count}\n\n"  \
        f"Ссылка для регистрации\n {game.link}\n"

    await callback.message.answer(text=message_text)
    await state.set_state(FSMAdminForm.group_confirm)


# Ветка оплаты
@router.message(F.text == LEXICON['payment'], StateFilter(default_state))
async def get_payment(message: Message, state: FSMContext):
    # Картинка спасибо за донат
    text_message = "Пора сделать подарок создателям бота\n\n"
    kb = [
        [InlineKeyboardButton(text='Задонатить 100 руб.',
                              callback_data='payment')]
    ]
    await message_send_photo(message, 'Scrooge.jpg')
    await message.answer(
        text=text_message,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )
    await state.set_state(FSMPaymentForm.payment)


@router.callback_query(StateFilter(FSMPaymentForm.payment))
async def get_donat(callback: CallbackQuery, state: FSMContext):
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title='Донат',
        description='Ты творишь добро',
        payload='что-то про payload',
        provider_token=settings.YOUKASSA_PAYMENT_TOKEN,
        currency="RUB",
        start_parameter="test_bot",
        prices=[LabeledPrice(label="руб", amount=10000)]
    )
    await state.set_state(FSMPaymentForm.invoice)
    await state.clear()


# @router.message(StateFilter(FSMPaymentForm.invoice))
# async def send_payment(message: Message, state: FSMContext):
#     print(1)


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
