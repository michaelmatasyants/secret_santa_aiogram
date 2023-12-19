from aiogram import Bot, types
from aiogram. import Payment, PaymentProvider
from aiogram import Bot
from santa_bot.bot.LEXICON import LEXICON

bot = Bot(token="YOUR_BOT_TOKEN")

# Подключение платежной системы
provider = PaymentProvider.YANDEX_MONEY
provider.setup(token="YOUR_YANDEX_MONEY_TOKEN")

# Обработка платежей
@bot.on(types.Message(commands=["pay"]))
async def pay(message: types.Message):
    # Создание запроса на оплату
    payment = provider.create_payment_request(
        amount=100,
        currency="RUB",
        invoice_id="1234567890",
        caption="Оплата подписки",
        description="Оплата подписки на месяц",
    )

    # Отправка запроса пользователю
    await message.reply(payment.start_url)

    # Обработка ответа от пользователя
    payment_update = await bot.get_updates()
    if payment_update.message.data == payment.id:
        # Обработка успешной оплаты
    elif payment_update.message.data == payment.failure_id:
        # Обработка неуспешной оплаты