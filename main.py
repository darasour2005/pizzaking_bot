import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web
from woocommerce import API

# --- PHSAR.ME PRO CONFIG ---
API_TOKEN = '8581539352:AAGByoBXhKj26xq2WPZkMdtsIUeYfpaDg6A'
WC_URL = "https://1.phsar.me"
WC_KEY = "ck_6a9c8caa18a2b0ab114ef90bb9e982d69521ec03"
WC_SECRET = "cs_63c256e1b4eba0a65723f054159e55d2148c3c57"
MERCHANT_ID = "alex@acleda" # Your Bakong/ACLEDA ID

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

# In-memory cart for multiple items
user_carts = {}

wcapi = API(url=WC_URL, consumer_key=WC_KEY, consumer_secret=WC_SECRET, version="wc/v3", timeout=15)

# --- RENDER HEARTBEAT ---
async def handle(request): return web.Response(text="Pizz King Pro v2 Online")
async def start_heartbeat():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()

# --- HELPER: KHQR GENERATOR ---
def get_pay_link(amount, name="Order"):
    # Clean amount for URL (no commas)
    clean_amt = str(amount).replace(",", "")
    return f"https://link.bakong.nbc.gov.kh/pay?id={MERCHANT_ID}&amount={clean_amt}&currency=KHR&name={name}"

# --- BOT ENTRY (LOAD PRODUCTS IMMEDIATELY) ---
@router.message(Command("start"))
async def start_handler(message: types.Message, command: CommandObject):
    # If drama link (start=ID)
    if command.args and command.args.isdigit():
        await show_product_detail(message, command.args)
        return

    # Show persistent Menu at bottom of phone
    main_menu = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛍️ មើលទំនិញទាំងអស់ (View Shop)")],
        [KeyboardButton(text="🛒 កន្ត្រករបស់ខ្ញុំ (My Cart)"), KeyboardButton(text="📞 ជំនួយ (Help)")]
    ], resize_keyboard=True)

    await message.answer("🇰🇭 ស្វាគមន៍មកកាន់ហាងរបស់យើង! រីករាយនឹងការទិញទំនិញ៖", reply_markup=main_menu)
    await show_shop(message, page=1)

@router.message(F.text == "🛍️ មើលទំនិញទាំងអស់ (View Shop)")
async def shop_btn(message: types.Message):
    await show_shop(message, page=1)

@router.message(F.text == "🛒 កន្ត្រករបស់ខ្ញុំ (My Cart)")
async def cart_btn(message: types.Message):
    await view_cart(message)

# --- THE SHOP (Infinite Scroll Style) ---
async def show_shop(message, page=1):
    products = wcapi.get("products", params={"per_page": 10, "page": page, "status": "publish"}).json()
    
    if not products:
        await message.answer("អស់ទំនិញហើយ! (No more products)")
        return

    for p in products:
        # Currency: Assume WC is in KHR or we append ៛
        price_display = f"{p['price']} ៛"
        img_url = p['images'][0]['src'] if p['images'] else None
        
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⚡ ទិញភ្លាមៗ (Buy Now)", url=get_pay_link(p['price'], "PhsarMe")),
                InlineKeyboardButton(text="➕ ដាក់កន្ត្រក", callback_data=f"add_{p['id']}")
            ],
            [InlineKeyboardButton(text="🔍 មើលលម្អិត (Details)", callback_data=f"detail_{p['id']}")]
        ])
        
        desc = f"📦 **{p['name']}**\n💰 តម្លៃ: **{price_display}**"
        if img_url:
            await bot.send_photo(message.chat.id, photo=img_url, caption=desc, reply_markup=markup, parse_mode="Markdown")
        else:
            await message.answer(desc, reply_markup=markup, parse_mode="Markdown")

    # Navigation at the bottom
    nav_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ បង្ហាញទំនិញថែមទៀត (Show More)", callback_data=f"more_{page+1}")]
    ])
    await message.answer("👇 ចុចខាងក្រោមដើម្បីមើលទំនិញបន្តទៀត៖", reply_markup=nav_markup)

@router.callback_query(F.data.startswith("more_"))
async def more_products(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[1])
    await callback.answer()
    await show_shop(callback.message, page=page)

# --- PRODUCT DETAIL & CART ---
async def show_product_detail(message, product_id):
    p = wcapi.get(f"products/{product_id}").json()
    price = p['price']
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ បង់ប្រាក់ឥឡូវនេះ (Buy Now)", url=get_pay_link(price, "DirectBuy"))],
        [InlineKeyboardButton(text="➕ ដាក់ចូលកន្ត្រក (Add to Cart)", callback_data=f"add_{product_id}")],
        [InlineKeyboardButton(text="🛍️ ត្រឡប់ទៅហាងវិញ", callback_data="more_1")]
    ])
    
    desc = f"✨ **{p['name']}**\n💰 តម្លៃ: **{price} ៛**\n\n{p.get('short_description', '').replace('<p>','').replace('</p>','')}"
    await message.answer(desc, reply_markup=markup, parse_mode="Markdown")

@router.callback_query(F.data.startswith("add_"))
async def add_to_cart(callback: types.CallbackQuery):
    p_id = callback.data.split("_")[1]
    user_id = callback.from_user.id
    if user_id not in user_carts: user_carts[user_id] = []
    
    p = wcapi.get(f"products/{p_id}").json()
    user_carts[user_id].append({"name": p['name'], "price": float(p['price'])})
    
    await callback.answer(f"✅ បន្ថែម {p['name']} រួចរាល់!")

async def view_cart(message):
    user_id = message.from_user.id
    cart = user_carts.get(user_id, [])
    if not cart:
        await message.answer("កន្ត្រកទទេ! សូមជ្រើសរើសទំនិញជាមុនសិន។")
        return
    
    total = sum(item['price'] for item in cart)
    text = "🛒 **កន្ត្រកទំនិញរបស់អ្នក:**\n\n"
    for i, item in enumerate(cart):
        text += f"{i+1}. {item['name']} - {item['price']} ៛\n"
    
    text += f"\n💰 **សរុប: {total} ៛**"
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 បង់ប្រាក់ទាំងអស់ (Checkout)", url=get_pay_link(total, "PhsarMeCart"))],
        [InlineKeyboardButton(text="🗑️ លុបកន្ត្រក", callback_data="clear_cart")]
    ])
    await message.answer(text, reply_markup=markup, parse_mode="Markdown")

@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: types.CallbackQuery):
    user_carts[callback.from_user.id] = []
    await callback.answer("លុបកន្ត្រករួចរាល់!")
    await callback.message.edit_text("កន្ត្រកទំនិញត្រូវបានលុប។")

# --- SYSTEM IGNITION ---
async def main():
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    await start_heartbeat()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
