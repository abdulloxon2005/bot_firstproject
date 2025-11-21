import asyncio
from aiogram import Bot,Dispatcher
from config import BOT_TOKEN
from handlers import start


async def main():
    bot = Bot(BOT_TOKEN)
    dp=Dispatcher()
    dp.include_router(start.router)


    print("bot ishladi")
    await dp.start_polling(bot)

asyncio.run(main())