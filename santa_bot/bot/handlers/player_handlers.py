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


class FSMUserForm(StatesGroup):
    name_group = State()
    description_group = State()
    choose_date = State()
    choose_price = State()
    get_link = State()
