import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# بارگذاری فایل .env
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN or not BOT_TOKEN.strip():
    raise ValueError("✗ BOT_TOKEN خالی یا نامعتبر است.")

bot = Bot(token=BOT_TOKEN.strip())
dp = Dispatcher()

# --- کتاب‌ها (کش شده با FSInputFile) ---
books = {
    "بوعلی سینا": {
        "id": "avicenna",  # شناسه ساده برای callback_data
        "desc": "آثار و نوشته‌های ارزشمند بوعلی سینا در زمینه فلسفه و پزشکی.",
        "photo": FSInputFile("Screenshot 2025-12-04 123009.png"),   # عکس داخل پوشه اصلی
        "pdf": FSInputFile(os.path.join("books", "بوعلی سینا.pdf")) # PDF داخل پوشه books
    }
}

# --- start ---
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("سلام! ربات فروش کتاب‌های کمیاب آماده‌ست 📚")

# --- catalog ---
@dp.message(Command("catalog"))
async def catalog_handler(message: Message):
    if not books:
        await message.answer("📭 هنوز کتابی ثبت نشده.")
        return

    for name, info in books.items():
        text = f"📖 {name}\n📝 {info['desc']}"
        buttons = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📥 دریافت رایگان", callback_data=f"free_{info['id']}")]
        ])
        await message.answer_photo(photo=info["photo"], caption=text, reply_markup=buttons)

# --- books ---
@dp.message(Command("books"))
async def show_books(message: types.Message):
    if not books:
        await message.answer("📭 هنوز کتابی ثبت نشده.")
        return

    keyboard = InlineKeyboardMarkup()
    for name, info in books.items():
        keyboard.add(InlineKeyboardButton(text=name, callback_data=f"book_{info['id']}"))
    await message.answer("📚 لیست کتاب‌ها:", reply_markup=keyboard)

# --- جزئیات کتاب ---
@dp.callback_query(lambda c: c.data.startswith("book_"))
async def book_detail(callback: types.CallbackQuery):
    book_id = callback.data.replace("book_", "")
    for name, info in books.items():
        if info["id"] == book_id:
            text = f"📖 {name}\n💰 قیمت: 45,000 تومان\n📝 توضیح: {info['desc']}"
            buttons = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📥 دریافت رایگان", callback_data=f"free_{info['id']}")]
            ])
            await callback.message.answer_photo(photo=info["photo"], caption=text, reply_markup=buttons)
            break
    await callback.answer()

# --- ارسال PDF ---
@dp.callback_query(lambda c: c.data.startswith("free_"))
async def send_book(callback: types.CallbackQuery):
    book_id = callback.data.replace("free_", "")
    for name, info in books.items():
        if info["id"] == book_id:
            await callback.message.answer_document(
                document=info["pdf"],
                caption=f"📖 نسخه رایگان {name}"
            )
            break
    await callback.answer()

# --- اجرای ربات ---
async def main():
    print("✅ ربات روشن شد. منتظر پیام‌ها هستم...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())