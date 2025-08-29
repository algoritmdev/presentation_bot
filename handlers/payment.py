from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from sqlalchemy.future import select
from database import async_session
from models import Purchase, Presentation
from utils.keyboards import approve_buttons, back_button
from config import ADMINS, CARD_NUMBER
from utils.helpers import temp_message, safe_edit

router = Router()

# 🛒 Sotib olish bosilganda
@router.callback_query(F.data.startswith("buy:"))
async def buy_callback(callback: CallbackQuery):
    pres_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        pres = await session.get(Presentation, pres_id)
        if not pres:
            msg = await callback.message.answer("❌ Slayd topilmadi.", reply_markup=back_button("main_menu"))
            await temp_message(msg, 3)
            return
        purchase = Purchase(user_id=callback.from_user.id, presentation_id=pres.id)
        session.add(purchase)
        await session.commit()

    await safe_edit(
        callback.message,
        f"🧾 To‘lov ma’lumotlari:\n💳 {CARD_NUMBER}\n💰 {pres.price} so‘m\n\n👉 To‘lovni amalga oshirib, chekni yuboring.",
        reply_markup=back_button("main_menu")
    )

# 📸 User chek yuborganda
@router.message(F.photo)
async def payment_proof(message: types.Message):
    await message.delete()
    async with async_session() as session:
        purchase = await session.scalar(
            select(Purchase)
            .where(Purchase.user_id == message.from_user.id)
            .where(Purchase.status == "pending")
        )
        if not purchase:
            msg = await message.answer("❌ Sizda kutilayotgan to‘lov yo‘q.", reply_markup=back_button("main_menu"))
            await temp_message(msg, 3)
            return

        purchase.payment_proof = message.photo[-1].file_id
        await session.commit()

        # Adminlarga yuborish
        for admin in ADMINS:
            await message.bot.send_photo(
                chat_id=admin,
                photo=message.photo[-1].file_id,
                caption=f"💳 To‘lov cheki\n👤 User: {message.from_user.id}\n🛒 Purchase ID: {purchase.id}",
                reply_markup=approve_buttons(purchase.id)
            )

    msg = await message.answer("✅ Chekingiz qabul qilindi. Admin tasdiqlashini kuting.", reply_markup=back_button("main_menu"))
    await temp_message(msg, 3)

# 🔁 Sotib olishdan keyingi tugmalar
@router.callback_query(F.data == "buy_more")
async def buy_more(callback: CallbackQuery):
    await safe_edit(callback.message, "🔎 Slayd nomini yoki narxini yozib qidiring.")

@router.callback_query(F.data == "finish")
async def finish(callback: CallbackQuery):
    await safe_edit(callback.message, "✅ Xarid jarayoni yakunlandi. Rahmat!")
