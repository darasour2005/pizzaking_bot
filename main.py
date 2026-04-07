import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# --- PIZZ KING ARCHITECTURE ---
API_TOKEN = '8581539352:AAGByoBXhKj26xq2WPZkMdtsIUeYfpaDg6A'
# Replace with your actual Bakong/ACLEDA ID (e.g., yourname@acleda)
MERCHANT_ID = "pizzking@acleda" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

# --- 1. RENDER HEARTBEAT (Prevents Build Errors) ---
async def handle(request):
    return web.Response(text="Pizz King Bot is Ignite!")

async def start_heartbeat():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Heartbeat online on port {port}")

# --- 2. BOT LOGIC (Khmer Priority) ---
@router.message(Command("start"))
async def start_handler(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍕 មើលមុខម្ហូប (View Menu)", callback_data="view_menu")],
        [InlineKeyboardButton(text="📞 ទំនាក់ទំនង (Contact)", url="https://t.me/your_personal_username")]
    ])
    
    await message.answer(
        "ស្វាគមន៍មកកាន់ **Pizz King Store**! 🇰🇭\n"
        "យើងមានផលិតផលពិសេសសម្រាប់អ្នកទស្សនា Drama!\n\n"
        "សូមជ្រើសរើសខាងក្រោម៖",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@router.callback_query(lambda c: c.data == "view_menu")
async def menu_handler(callback: types.CallbackQuery):
    # Example product: You can add more here easily
    text = "🛍️ **ផលិតផលពិសេសថ្ងៃនេះ**\n\n1. Drama Pizza - $10.00\n2. Special Tea - $2.00"
    
    # KHQR Deep Link Logic: This opens the ACLEDA/Bakong app directly on the phone!
    pay_link = f"https://link.bakong.nbc.gov.kh/pay?id={MERCHANT_ID}&amount=10.00&currency=USD&name=Pizz%20King"
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 ទិញ Pizza ($10)", url=pay_link)],
        [InlineKeyboardButton(text="🔙 ត្រឡប់ក្រោយ", callback_data="start_over")]
    ])
    
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")

# --- 3. SYSTEM IGNITION ---
async def main():
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    
    # Start the web server and the bot at the same time
    await start_heartbeat()
    print("Architect Core: Bot starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
