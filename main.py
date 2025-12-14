import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# ---------------- SOZLAMALAR ----------------
BOT_TOKEN = "8557329766:AAHzDhR3sPmcGVS3bhhdjET4l7EBLQQ7S90"
# Kanal ID o'rniga to'g'ridan-to'g'ri nomini yozamiz (qo'shtirnoq ichida bo'lsin)
CHANNEL_ID = "@Shohjahon12uz_PUBG" 
KARTA_RAQAM = "4073 4200 4179 5174 (MADINA UBAYDULLAYEVA)"
NARX = "5 000 so'm"
# --------------------------------------------

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Holatlar
class Xarid(StatesGroup):
    chek_kutish = State()

# Tugmalar
main_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="💎 Aternos 24/7 olish")]],
    resize_keyboard=True
)

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Bekor qilish")]],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Salom! Aternos serveringiz 24/7 ishlashi uchun xizmatni sotib oling.\nNarxi: {NARX}",
        reply_markup=main_menu
    )

# 1. Sotib olish bosilganda
@dp.message(F.text == "💎 Aternos 24/7 olish")
async def start_buy(message: types.Message, state: FSMContext):
    await message.answer(
        f"To'lov kartasi: <b>{KARTA_RAQAM}</b>\nNarxi: <b>{NARX}</b>\n\n"
        f"To'lov qilib, chekni (skrinshotni) shu yerga yuboring.",
        parse_mode="HTML",
        reply_markup=cancel_kb
    )
    await state.set_state(Xarid.chek_kutish)

# 2. Bekor qilish
@dp.message(F.text == "Bekor qilish")
async def cancel_process(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Bekor qilindi.", reply_markup=main_menu)

# 3. Rasm kelganda (KANALGA YUBORISH)
@dp.message(Xarid.chek_kutish, F.photo)
async def handle_photo(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    # Kanal uchun tugmalar
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"ok_{user_id}"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"no_{user_id}")
        ]
    ])
    
    await message.answer("Chek qabul qilindi! Kanal adminlari tasdiqlashini kuting...", reply_markup=main_menu)
    
    # Kanalga yuborish
    try:
        await bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=message.photo[-1].file_id,
            caption=f"💰 <b>YANGI TO'LOV!</b>\n\nMijoz: {message.from_user.full_name}\nUsername: @{message.from_user.username}\nID: <code>{user_id}</code>",
            parse_mode="HTML",
            reply_markup=admin_kb
        )
    except Exception as e:
        await message.answer(f"Xatolik: Bot kanalga yubora olmadi. Botni kanalga ADMIN qiling!\nXato: {e}")
    
    await state.clear()

# 4. Kanalda "✅ Qabul qilish" bosilganda
@dp.callback_query(F.data.startswith("ok_"))
async def accept_pay(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    
    # Kanalda xabarni o'zgartirish
    await callback.message.edit_caption(
        caption=f"{callback.message.caption}\n\n✅ TASDIQLANDI (Admin: {callback.from_user.first_name})", 
        reply_markup=None
    )
    
    # Mijozga xabar
    try:
        await bot.send_message(
            chat_id=user_id,
            text="✅ <b>To'lov tasdiqlandi!</b>\n\nEndi serveringizni ulash uchun <b>IP manzili</b> va <b>Portini</b> yozib yuboring.\nMisol: <code>server.aternos.me:12345</code>",
            parse_mode="HTML"
        )
    except:
        pass

# 5. Kanalda "❌ Bekor qilish" bosilganda
@dp.callback_query(F.data.startswith("no_"))
async def deny_pay(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    
    await callback.message.edit_caption(
        caption=f"{callback.message.caption}\n\n❌ RAD ETILDI (Admin: {callback.from_user.first_name})", 
        reply_markup=None
    )
    
    try:
        await bot.send_message(user_id, "❌ To'lovingiz rad etildi.")
    except:
        pass

# 6. Mijoz IP yozganda (Uni ham kanalga tashlaymiz)
@dp.message(F.text)
async def forward_ip(message: types.Message):
    if message.text not in ["💎 Aternos 24/7 olish", "Bekor qilish", "/start"]:
        # Mijoz yozgan IP ni kanalga tashlash
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"📩 <b>MIJOZDAN MA'LUMOT (IP):</b>\n\n{message.text}\n\nMijoz ID: <code>{message.from_user.id}</code>",
            parse_mode="HTML"
        )
        await message.answer("Ma'lumot adminga yuborildi! Tez orada ulab beramiz. ✅")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())