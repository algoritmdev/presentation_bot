from aiogram import Router, types, F
from sqlalchemy.future import select
from database import async_session
from models import Presentation
from utils.keyboards import pagination_keyboard, back_button
from utils.helpers import temp_message, normalize_text, safe_edit
import math

router = Router()
PAGE_SIZE = 5

async def get_presentations(query: str):
    async with async_session() as session:
        stmt = select(Presentation).where(Presentation.title.ilike(f"%{query}%"))
        result = await session.execute(stmt)
        return result.scalars().all()

@router.message(F.text & ~F.text.startswith("/"))
async def search_handler(message: types.Message):
    query = normalize_text(message.text)
    await message.delete()
    presentations = await get_presentations(query)
    if not presentations:
        msg = await message.answer("❌ Hech narsa topilmadi.", reply_markup=back_button("main_menu"))
        await temp_message(msg, 3)
        return
    await send_page(message, presentations, query, page=1)

@router.callback_query(F.data.startswith("page:"))
async def page_callback(callback: types.CallbackQuery):
    _, page, query = callback.data.split(":", maxsplit=2)
    page = int(page)
    presentations = await get_presentations(query)
    await send_page(callback.message, presentations, query, page, edit=True)
    await callback.answer()

async def send_page(message, presentations, query, page=1, edit=False):
    total_pages = max(1, math.ceil(len(presentations) / PAGE_SIZE))
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    items = presentations[start:end]

    text = f"🔎 Qidiruv natijalari ({page}/{total_pages}):\n\n"
    for p in items:
        text += f"📄 {p.title}\n💰 {p.price} so‘m\n\n"

    kb = pagination_keyboard(page, total_pages, query, [p.id for p in items])

    if edit:
        await safe_edit(message, text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)
