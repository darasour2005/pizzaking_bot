import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web
from woocommerce import API

# --- PHSAR.ME APP-STYLE CONFIG ---
API_TOKEN = '8581539352:AAGByoBXhKj26xq2WPZkMdtsIUeYfpaDg6A'
WC_URL = "https://1.phsar.me"
WC_KEY = "ck_6a9c8caa18a2b0ab114ef90bb9e982d69521ec03"
WC_SECRET = "cs_63c256e1b4eba0a65723f054159e55d2148c3c57"
MERCHANT_ID = "alex@acleda" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

# user_data[user_id] = {"qty": {p_id: count}, "cart": []}
user_states = {}

wcapi = API(url=WC_URL, consumer_key=WC_KEY, consumer_secret=WC_SECRET, version="wc/v3", timeout=15)

# --- 1. SINGLE-LINE APP MENU (Bottom Bar) ---
def get_app_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🏠 Home"), KeyboardButton(text="🛒 Cart"), KeyboardButton(text="📞 Contact")]
    ], resize_keyboard=True)

# --- 2. PRODUCT CARDS (App Layout) ---
async def load_app_products(message, page=1):
    products = wcapi.get("products", params={"per_page": 6, "page": page, "status": "publish"}).json()
    
    for p in products:
        p_id = p['id']
        price = p.get('sale_price') if p.get('on_sale') else p.get('regular_price')
        old_price = p.get('regular_price') if p.get('on_sale') else ""
        
        # Display: ~~100៛~~ 🔥 80៛
        price_tag = f"🔥 **{price}៛**"
        if old_price: price_tag = f"~~{old_price}៛~~ {price_tag}"

        # 2-Column Button Layout with Icons
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⚡ Buy Now", url=f"https://link.bakong.nbc.gov.kh/pay?id={MERCHANT_ID}&amount={price}&currency=KHR"),
                InlineKeyboardButton(text="➕ Add", callback_data=f"cart_{p_id}")
            ],
            [
                InlineKeyboardButton(text="➖", callback_data=f"qty_minus_{p_id}"),
                InlineKeyboardButton(text="1", callback_data=f"qty_val_{p_id}"), # QTY indicator
                InlineKeyboardButton(text="➕", callback_data=f"qty_plus_{p_id}")
            ],
            [InlineKeyboardButton(text="🔍", callback_data=f"detail_{p_id}")] # Magnify Icon for details
        ])

        caption = f"📦 **{p['name']}**\n💰 {price_tag}"
        img_url = p['images'][0]['src'] if p['images'] else None

        if img_url:
            await bot.send_photo(message.chat.id, photo=img_url, caption=caption, reply_markup=markup, parse_mode="Markdown")
        else:
            await message.answer(caption, reply_markup=markup, parse_mode="Markdown")

    # App-style "See More" at bottom
    next_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="👇 Show More Products", callback_data=f"more_{page+1}")]])
    await message.answer("--- End of Page ---", reply_markup=next_btn)

# --- 3. BOT IGNITION & HANDLERS ---
@router.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("🚀 **Pizz King App Online**", reply_markup=get_app_menu())
    await load_app_products(message, page=1)

@router.message(F.text == "🏠 Home")
async def home_handler(message: types.Message):
    await load_app_products(message, page=1)

@router.callback_query(F.data.startswith("qty_"))
async def handle_qty(callback: types.CallbackQuery):
    # This simulates a QTY picker by updating the button text
    await callback.answer("Updating Quantity...")
    # (In a real build, we save the number in user_states and refresh the markup)

@router.callback_query(F.data.startswith("more_"))
async def more_handler(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[1])
    await callback.answer()
    await load_app_products(callback.message, page=page)

# --- RENDER HEARTBEAT ---
async def handle(request): return web.Response(text="App Online")
async def start_heartbeat():
    app = web.Application(); app.router.add_get("/", handle)
    runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()

async def main():
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    await start_heartbeat()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
