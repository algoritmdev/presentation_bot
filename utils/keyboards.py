from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def back_button(callback_data: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Ortga", callback_data=callback_data)]]
    )

def approve_buttons(purchase_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve:{purchase_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject:{purchase_id}")
            ]
        ]
    )

def pagination_keyboard(page, total_pages, query, pres_ids):
    kb = []
    for pres_id in pres_ids:
        kb.append([InlineKeyboardButton(text="🛒 Sotib olish", callback_data=f"buy:{pres_id}")])

    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"page:{page-1}:{query}"))
    if page < total_pages:
        nav.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"page:{page+1}:{query}"))
    if nav:
        kb.append(nav)

    kb.append([InlineKeyboardButton(text="⬅️ Bosh menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# 🆕 Sotib olishdan keyingi tugmalar
def after_purchase_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Yana slayd sotib olish", callback_data="buy_more")],
            [InlineKeyboardButton(text="❌ Yo‘q, tugatish", callback_data="finish")]
        ]
    )
