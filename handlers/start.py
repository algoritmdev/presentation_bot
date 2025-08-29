from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.future import select
from database import async_session
from models import User

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == message.from_user.id))
        if not user:
            user = User(user_id=message.from_user.id)
            session.add(user)
            await session.commit()
    await message.answer("👋 Xush kelibsiz!\nSlayd qidirish uchun matn yozing.")
