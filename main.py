import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web
from woocommerce import API

# --- CONFIGURATION ---
API_TOKEN = '8581539352:AAGByoBXhKj26xq2WPZkMdtsIUeYfpaDg6A'
WC_URL = "https://1.phsar.me"
WC_KEY = "ck_6a9c8caa18a2b0ab114ef90bb9e982d69521ec03"
WC_SECRET = "cs_63c256e1b4eba0a65723f054159e55d2148c3c57"
MERCHANT_ID = "alex@acleda" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

# Simple In-Memory Cart (User ID -> List of Items)
# Pro Note: In production, use a Database, but for 1000 items this is fast.
user_carts = {}

wcapi = API(url=WC_URL, consumer_key=WC_KEY, consumer_secret=WC_SECRET, version="wc/v3", timeout=15)

# --- 1. RENDER HEARTBEAT ---
async def handle(request): return web.Response(text="Pizz King Pro is Ignite!")
async def start_heartbeat():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()

# --- 2. PAGINATION LOGIC (The "1000 Items" Solution) ---
@router.message(Command("start"))
async def start_handler(message: types.Message, command: CommandObject):
    # Support for Drama Links (t.me/bot?start=ID)
    if command.args and command.args.isdigit():
        await show_product_detail(message, command.args)
        return
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ ចូលហាងទំនិញ (Enter Store)", callback_data="shop_1")],
        [InlineKeyboardButton(text="🛒 កន្ត្រកទំនិញ (My Cart)", callback_data="view_cart")]
    ])
    await message.answer("ស្វាគមន៍មកកាន់ **Pizz King Pro**!\nសូមជ្រើសរើស៖", reply_markup=markup, parse_mode="Markdown")

@router.callback_query(F.data.startswith("shop_"))
async def shop_pagination(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[1])
    await callback.answer(f"កំពុងទាញយកទំព័រទី {page}...")
    
    # Fetch 8 items for the specific page
    products = wcapi.get("products", params={"per_page": 8, "page": page, "status": "publish"}).json()
    
    if not products:
        await callback.message.answer("អស់ទំនិញហើយ! (No more products)")
        return

    buttons = []
    for p in products:
        buttons.append([InlineKeyboardButton(text=f"{p['name']} - ${p['price']}", callback_data=f"detail_{p['id']}")])
    
    # Navigation Buttons
    nav_row = []
    if page > 1: nav_row.append(InlineKeyboardButton(text="⬅️ Back", callback_data=f"shop_{page-1}"))
    nav_row.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"shop_{page+1}"))
    buttons.append(nav_row)
    buttons.append([InlineKeyboardButton(text="🏠 Menu", callback_data="main_menu")])
    
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(f"📖 ទំព័រទី {page} (Items 1-1000)", reply_markup=markup)

# --- 3. CART SYSTEM (Multiple Items) ---
@router.callback_query(F.data.startswith("add_"))
async def add_to_cart(callback: types.CallbackQuery):
    p_id = callback.data.split("_")[1]
    user_id = callback.from_user.id
    
    if user_id not in user_carts: user_carts[user_id] = []
    
    # Fetch item to get name and price
    p = wcapi.get(f"products/{p_id}").json()
    user_carts[user_id].append({"id": p_id, "name": p['name'], "price": float(p['price'])})
    
    await callback.answer(f"✅ បានបន្ថែម {p['name']} ទៅក្នុងកន្ត្រក!")

@router.callback_query(F.data == "view_cart")
async def view_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    cart = user_carts.get(user_id, [])
    
    if not cart:
        await callback.message.answer("កន្ត្រករបស់អ្នកគឺទទេ! (Cart is empty)")
        return
    
    total = sum(item['price'] for item in cart)
    text = "🛒 **កន្ត្រកទំនិញរបស់អ្នក:**\n\n"
    for i, item in enumerate(cart):
        text += f"{i+1}. {item['name']} - ${item['price']}\n"
    
    text += f"\n💰 **សរុបរួម: ${total:.2f}**"
    
    # Generate Total Payment QR
    pay_link = f"https://link.bakong.nbc.gov.kh/pay?id={MERCHANT_ID}&amount={total}&currency=USD&name=PizzKingStore"
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 បង់ប្រាក់សរុប (Pay Total)", url=pay_link)],
        [InlineKeyboardButton(text="🗑️ លុបកន្ត្រក (Clear Cart)", callback_data="clear_cart")],
        [InlineKeyboardButton(text="🛍️ បន្តទិញទំនិញ", callback_data="shop_1")]
    ])
    await callback.message.answer(text, reply_markup=markup, parse_mode="Markdown")

# --- 4. IMAGE FIX & DETAIL ---
async def show_product_detail(message, product_id):
    p = wcapi.get(f"products/{product_id}").json()
    name, price = p.get('name'), p.get('price')
    
    # PULSE-VERIFY: Fixed Image Path (reaching deep into the WooCommerce list)
    images = p.get('images', [])
    img_url = images[0].get('src') if images else None

    detail_text = f"✨ **{name}**\n💰 តម្លៃ: ${price}\n\nសូមចុច Add to Cart ដើម្បីទិញច្រើនមុខ"
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add to Cart", callback_data=f"add_{product_id}")],
        [InlineKeyboardButton(text="🛒 មើលកន្ត្រក (View Cart)", callback_data="view_cart")],
        [InlineKeyboardButton(text="🔙 Back to Shop", callback_data="shop_1")]
    ])

    if img_url:
        await bot.send_photo(message.chat.id, photo=img_url, caption=detail_text, reply_markup=markup, parse_mode="Markdown")
    else:
        await message.answer(detail_text, reply_markup=markup)

@router.callback_query(F.data.startswith("detail_"))
async def detail_callback(callback: types.CallbackQuery):
    await show_product_detail(callback.message, callback.data.split("_")[1])

@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: types.CallbackQuery):
    user_carts[callback.from_user.id] = []
    await callback.answer("កន្ត្រកត្រូវបានលុប!")
    await callback.message.edit_text("កន្ត្រកទំនិញគឺទទេ (Cart Cleared).")

# --- SYSTEM START ---
async def main():
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    await start_heartbeat()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
