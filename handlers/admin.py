from aiogram import Router, F
from aiogram.types import CallbackQuery
from database import async_session
from models import Purchase, Presentation
from config import CHANNEL_ID
from utils.keyboards import back_button, after_purchase_keyboard
from utils.helpers import safe_edit

router = Router()

# ✅ Admin tasdiqlashi
@router.callback_query(F.data.startswith("approve:"))
async def approve_purchase(callback: CallbackQuery):
    purchase_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        purchase = await session.get(Purchase, purchase_id)
        if not purchase:
            return
        purchase.status = "approved"
        await session.commit()

        pres = await session.get(Presentation, purchase.presentation_id)

        # Userga fayl yuboriladi
        await callback.bot.copy_message(
            chat_id=purchase.user_id,
            from_chat_id=CHANNEL_ID,
            message_id=pres.channel_msg_id,
            caption=""  # caption saqlanadi
        )

        # Userga tanlov tugmalari chiqadi
        await callback.bot.send_message(
            purchase.user_id,
            "Yana slayd sotib olasizmi?",
            reply_markup=after_purchase_keyboard()
        )

    # Admin xabari yangilanadi
    await safe_edit(callback.message, "✅ To‘lov tasdiqlandi.", reply_markup=back_button("admin_menu"))

# ❌ Admin rad etishi
@router.callback_query(F.data.startswith("reject:"))
async def reject_purchase(callback: CallbackQuery):
    purchase_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        purchase = await session.get(Purchase, purchase_id)
        if not purchase:
            return
        purchase.status = "rejected"
        await session.commit()

    await safe_edit(callback.message, "❌ To‘lov rad etildi.", reply_markup=back_button("admin_menu"))
