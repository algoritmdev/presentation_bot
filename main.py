import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN
from handlers import start, search, payment, admin, admin_panel, channel
from database import engine, Base
from handlers.admin_panel import admin_menu_keyboard
from utils.helpers import safe_edit

async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    dp.include_router(start.router)
    dp.include_router(admin_panel.router)
    dp.include_router(payment.router)
    dp.include_router(admin.router)
    dp.include_router(channel.router)
    dp.include_router(search.router)

    @dp.callback_query(F.data == "main_menu")
    async def back_to_main(callback: types.CallbackQuery):
        await safe_edit(callback.message, "🏠 Bosh menyuga qaytdingiz.\nSlayd qidirish uchun matn yozing.")

    @dp.callback_query(F.data == "admin_menu")
    async def back_to_admin(callback: types.CallbackQuery):
        await safe_edit(callback.message, "⚙️ Admin paneli:", reply_markup=admin_menu_keyboard())

    print("🤖 Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
