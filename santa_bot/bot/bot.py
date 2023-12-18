import asyncio

from aiogram import Bot, Dispatcher
from django.conf import settings

from .handlers import common_handlers, organizer_handlers, player_handlers


async def main():
    bot = Bot(settings.TELEGRAM_TOKEN)
    dp = Dispatcher()

    dp.include_routers(common_handlers.router, organizer_handlers.router, player_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

    async def get_link(chat_id: int):
        link = bot.create_chat_invite_link(chat_id)
        return link


if __name__ == '__main__':
    asyncio.run(main())
