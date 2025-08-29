from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.future import select
from database import async_session
from models import Presentation, Purchase
from config import ADMINS, update_card_number
from utils.keyboards import approve_buttons, back_button
from utils.helpers import safe_edit

router = Router()

# 💳 Karta raqamini o‘zgartirish uchun FSM
class CardFSM(StatesGroup):
    waiting_for_card = State()

# 🔘 Admin menyu tugmalari
def admin_menu_keyboard():
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="📂 Slaydlar", callback_data="list_presentations"),
                types.InlineKeyboardButton(text="💳 To‘lovlar", callback_data="list_purchases")
            ],
            [
                types.InlineKeyboardButton(text="📜 Tarix", callback_data="payment_history"),
                types.InlineKeyboardButton(text="💳 Kartani o‘zgartirish", callback_data="change_card")
            ],
            [types.InlineKeyboardButton(text="⬅️ Chiqish", callback_data="exit_panel")]
        ]
    )

# 🔑 Admin panelga kirish
@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMINS:
        await message.answer("❌ Siz admin emassiz.", reply_markup=back_button("main_menu"))
        return
    await message.answer("⚙️ Admin paneli:", reply_markup=admin_menu_keyboard())

# 📂 Slaydlar ro‘yxati
@router.callback_query(F.data == "list_presentations")
async def list_presentations(callback: types.CallbackQuery):
    async with async_session() as session:
        result = await session.execute(select(Presentation))
        presentations = result.scalars().all()
    if not presentations:
        await safe_edit(callback.message, "❌ Slaydlar yo‘q.", reply_markup=back_button("admin_menu"))
        return
    text = "📂 Slaydlar ro‘yxati:\n\n"
    for p in presentations:
        text += f"📄 {p.title} — 💰 {p.price} so‘m\n"
    await safe_edit(callback.message, text, reply_markup=back_button("admin_menu"))

# 💳 Kutilayotgan to‘lovlar
@router.callback_query(F.data == "list_purchases")
async def list_purchases(callback: types.CallbackQuery):
    async with async_session() as session:
        result = await session.execute(select(Purchase).where(Purchase.status == "pending"))
        purchases = result.scalars().all()
    if not purchases:
        await safe_edit(callback.message, "❌ Kutilayotgan to‘lovlar yo‘q.", reply_markup=back_button("admin_menu"))
        return
    for pur in purchases:
        caption = f"🆔 {pur.id}\n👤 User: {pur.user_id}\n📄 Slayd ID: {pur.presentation_id}"
        if pur.payment_proof:
            await callback.bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=pur.payment_proof,
                caption=caption,
                reply_markup=approve_buttons(pur.id)
            )
        else:
            await callback.message.answer(caption + "\n❌ Chek yuborilmagan.", reply_markup=approve_buttons(pur.id))

# 📜 To‘lovlar tarixi
@router.callback_query(F.data == "payment_history")
async def payment_history(callback: types.CallbackQuery):
    async with async_session() as session:
        result = await session.execute(select(Purchase).where(Purchase.status != "pending"))
        purchases = result.scalars().all()
    if not purchases:
        await safe_edit(callback.message, "❌ Hali to‘lovlar yo‘q.", reply_markup=back_button("admin_menu"))
        return
    text = "📜 To‘lovlar tarixi:\n\n"
    for pur in purchases:
        text += f"🆔 {pur.id} | 👤 {pur.user_id} | 📄 {pur.presentation_id} | 📌 {pur.status}\n"
    await safe_edit(callback.message, text, reply_markup=back_button("admin_menu"))

# 💳 Karta raqamini o‘zgartirish
@router.callback_query(F.data == "change_card")
async def ask_card_number(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit(callback.message, "💳 Yangi karta raqamini yuboring:", reply_markup=back_button("admin_menu"))
    await state.set_state(CardFSM.waiting_for_card)

@router.message(CardFSM.waiting_for_card)
async def save_card_number(message: types.Message, state: FSMContext):
    new_card = message.text.strip()
    if not new_card.replace(" ", "").isdigit():
        await message.answer("❌ Faqat raqam bo‘lishi kerak.", reply_markup=back_button("admin_menu"))
        return

    # .env faylini yangilash
    with open(".env", "r") as f:
        lines = f.readlines()
    with open(".env", "w") as f:
        found = False
        for line in lines:
            if line.startswith("CARD_NUMBER="):
                f.write(f"CARD_NUMBER={new_card}\n")
                found = True
            else:
                f.write(line)
        if not found:
            f.write(f"CARD_NUMBER={new_card}\n")

    update_card_number(new_card)
    await state.clear()
    await message.answer(f"✅ Karta raqami yangilandi: {new_card}", reply_markup=back_button("admin_menu"))

# ⬅️ Admin paneldan chiqish
@router.callback_query(F.data == "exit_panel")
async def exit_panel(callback: types.CallbackQuery):
    await safe_edit(callback.message, "⬅️ Admin paneldan chiqdingiz.", reply_markup=back_button("main_menu"))

# ↩️ Admin menyuga qaytish
@router.callback_query(F.data == "admin_menu")
async def back_to_admin(callback: types.CallbackQuery):
    await safe_edit(callback.message, "⚙️ Admin paneli:", reply_markup=admin_menu_keyboard())
