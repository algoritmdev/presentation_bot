from aiogram import Router, types, F
from database import async_session
from models import Presentation
from config import CHANNEL_ID
import asyncio

router = Router()

@router.channel_post(F.document | F.photo)
async def add_presentation_channel(message: types.Message):
    if message.chat.id != CHANNEL_ID:
        return

    caption = message.caption or ""
    if "/" not in caption:
        try:
            await message.bot.delete_message(CHANNEL_ID, message.message_id)
        except:
            pass
        return

    try:
        title, price_text = caption.split("/", maxsplit=1)
        title = title.strip()
        price = int(price_text.strip())
    except Exception:
        try:
            await message.bot.delete_message(CHANNEL_ID, message.message_id)
        except:
            pass
        return

    async with async_session() as session:
        session.add(Presentation(title=title, price=price, channel_msg_id=message.message_id))
        await session.commit()

    # ✅ Kanalga xabar chiqarish
    info_msg = await message.reply("✅ Slayd qo‘shildi!")
    await asyncio.sleep(2)
    try:
        await message.bot.delete_message(CHANNEL_ID, info_msg.message_id)
    except:
        pass
