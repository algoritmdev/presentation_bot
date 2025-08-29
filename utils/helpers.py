import asyncio
from aiogram import types

async def temp_message(msg, delay: int = 5):
    """Vaqtinchalik xabar chiqarib, keyin o‘chiradi"""
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass

def normalize_text(text: str) -> str:
    return text.lower()

async def safe_edit(message: types.Message, text: str, reply_markup=None):
    """
    Agar message text bo‘lsa edit_text, bo‘lmasa yangi answer yuboradi.
    """
    try:
        if message.text:
            await message.edit_text(text, reply_markup=reply_markup)
        else:
            await message.answer(text, reply_markup=reply_markup)
    except Exception as e:
        print("safe_edit error:", e)
        await message.answer(text, reply_markup=reply_markup)
