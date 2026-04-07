import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web
from woocommerce import API

# --- PHSAR.ME MOBILE APP CONFIG ---
API_TOKEN = '8581539352:AAGByoBXhKj26xq2WPZkMdtsIUeYfpaDg6A'
WC_URL = "https://1.phsar.me"
WC_KEY = "ck_6a9c8caa18a2b0ab114ef90bb9e982d69521ec03"
WC_SECRET = "cs_63c256e1b4eba0a65723f054159e55d2148c3c57"
MERCHANT_ID = "alex@acleda" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()
user_carts = {}

wcapi = API(url=WC_URL, consumer_key=WC_KEY, consumer_secret=WC_SECRET, version="wc/v3", timeout=15)

# --- APP NAVIGATION MENU (The "Bottom Bar") ---
def get_app_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🏠 Home"), KeyboardButton(text="🛒 Pay (Checkout)")],
        [KeyboardButton(text="⬅️ Back"), KeyboardButton(text="📞 Contact")]
    ], resize_keyboard=True)

# --- START: DIRECT PRODUCT INJECTION ---
@router.message(Command("start"))
async def start_handler(message: types.Message, command: CommandObject):
    # Reset page history for user
    if command.args and command.args.isdigit():
        await show_product_detail(message, command.args)
    else:
        await message.answer("🚀 ស្វាគមន៍មកកាន់ **Pizz King App**", reply_markup=get_app_menu())
        await load_app_page(message, page=1)

@router.message(F.text == "🏠 Home")
async def home_btn(message: types.Message):
    await load_app_page(message, page=1)

@router.message(F.text == "🛒 Pay (Checkout)")
async def pay_btn(message: types.Message):
    await view_app_cart(message)

@router.message(F.text == "📞 Contact")
async def contact_btn(message: types.Message):
    await message.answer("🙏 សម្រាប់ជំនួយ សូមទាក់ទងមកកាន់៖\n@your_telegram_id\nលេខទូរស័ព្ទ: 012 345 678")

# --- PRODUCT LISTING (With Sale Prices) ---
async def load_app_page(message, page=1):
    products = wcapi.get("products", params={"per_page": 8, "page": page, "status": "publish"}).json()
    
    for p in products:
        # Price Logic: Sale vs Regular
        reg_price = p.get('regular_price', '0')
        sale_price = p.get('sale_price', '')
        on_sale = p.get('on_sale', False)

        if on_sale and sale_price:
            price_text = f"~~{reg_price}៛~~ 🔥 **{sale_price}៛**"
            final_price = sale_price
        else:
            price_text = f"**{reg_price}៛**"
            final_price = reg_price

        img_url = p['images'][0]['src'] if p['images'] else None
        
        # UI Buttons: App Style
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⚡ Buy Now", url=f"https://link.bakong.nbc.gov.kh/pay?id={MERCHANT_ID}&amount={final_price}&currency=KHR"),
                InlineKeyboardButton(text="➕ Add to Cart", callback_data=f"add_{p['id']}")
            ],
            [InlineKeyboardButton(text="📖 View Details", callback_data=f"detail_{p['id']}")]
        ])
        
        caption = f"📦 **{p['name']}**\n💰 {price_text}"
        
        if img_url:
            await bot.send_photo(message.chat.id, photo=img_url, caption=caption, reply_markup=markup, parse_mode="Markdown")
        else:
            await message.answer(caption, reply_markup=markup, parse_mode="Markdown")

    # Load More Button
    nav = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="👇 មើលទំនិញបន្តទៀត", callback_data=f"more_{page+1}")]])
    await message.answer("--- បញ្ចប់ទំព័រ ---", reply_markup=nav)

# --- ADD TO CART LOGIC ---
@router.callback_query(F.data.startswith("add_"))
async def add_to_cart(callback: types.CallbackQuery):
    p_id = callback.data.split("_")[1]
    p = wcapi.get(f"products/{p_id}").json()
    user_id = callback.from_user.id
    
    if user_id not in user_carts: user_carts[user_id] = []
    
    price = p.get('sale_price') if p.get('on_sale') else p.get('regular_price')
    user_carts[user_id].append({"name": p['name'], "price": float(price)})
    
    await callback.answer(f"✅ {p['name']} Added!")

async def view_app_cart(message):
    user_id = message.from_user.id
    cart = user_carts.get(user_id, [])
    if not cart:
        await message.answer("កន្ត្រកទទេ! Cart is empty.")
        return
    
    total = sum(item['price'] for item in cart)
    text = "🛒 **កន្ត្រកទំនិញរបស់អ្នក:**\n\n"
    for i, item in enumerate(cart):
        text += f"{i+1}. {item['name']} - {item['price']}៛\n"
    text += f"\n💰 **សរុប: {total}៛**"
    
    pay_link = f"https://link.bakong.nbc.gov.kh/pay?id={MERCHANT_ID}&amount={total}&currency=KHR"
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Pay Now (ACLEDA/Bakong)", url=pay_link)],
        [InlineKeyboardButton(text="🗑️ Clear Cart", callback_data="clear_cart")]
    ])
    await message.answer(text, reply_markup=markup, parse_mode="Markdown")

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
