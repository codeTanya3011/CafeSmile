import asyncio
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from handlers.app import router

load_dotenv()
TOKEN = getenv('TOKEN')
PAY = getenv('PORTMONE')
MANAGER = getenv('MANAGER')
dp = Dispatcher()
# session = AiohttpSession(proxy="http://222.252.194.204:8080")
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode='HTML'))

dp.include_router(router)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

