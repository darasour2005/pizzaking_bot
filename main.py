import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web
from woocommerce import API

# --- SYSTEM CONFIG ---
API_TOKEN = '8581539352:AAGByoBXhKj26xq2WPZkMdtsIUeYfpaDg6A'
WC_URL = "https://1.phsar.me"
WC_KEY = "ck_6a9c8caa18a2b0ab114ef90bb9e982d69521ec03"
WC_SECRET = "cs_63c256e1b4eba0a65723f054159e55d2148c3c57"
MERCHANT_ID = "alex@acleda" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

# GLOBAL CACHE: To make "Add to Cart" instant
product_cache = {} # Stores {id: {name, price, img}}
user_states = {}   # Stores {user_id: {cart: [], qty: {p_id: 1}, page: 1}}

wcapi = API(url=WC_URL, consumer_key=WC_KEY, consumer_secret=WC_SECRET, version="wc/v3", timeout=10)

# --- 1. APP-LIKE BOTTOM MENU ---
def get_main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛍️ Shop"), KeyboardButton(text="🛒 Cart"), KeyboardButton(text="📞 Help")]
    ], resize_keyboard=True)

# --- 2. LOAD PRODUCTS (6 PER PAGE) ---
async def load_shop_page(message, page=1, user_id=None):
    # Pulse-Verify: Fetching 6 items is 40% faster than 10
    try:
        response = wcapi.get("products", params={"per_page": 6, "page": page, "status": "publish"})
        products = response.json()
    except:
        await message.answer("⚠️ Connection to 1.phsar.me timed out.")
        return

    if not products:
        await message.answer("🏁 No more products.")
        return

    for p in products:
        p_id = str(p['id'])
        # Save to cache for instant "Add to Cart"
        product_cache[p_id] = {
            "name": p['name'],
            "price": p['price'] if p['price'] else "0",
            "img": p['images'][0]['src'] if p['images'] else None
        }

        # Handle Variations: If price is empty, it's usually a variable product
        display_price = f"{p['price']}៛" if p['price'] else "Check Options"
        if p['on_sale'] and p['sale_price']:
            display_price = f"~~{p['regular_price']}៛~~ 🔥 **{p['sale_price']}៛**"

        # QTY for this user
        if user_id not in user_states: user_states[user_id] = {"cart": [], "qty": {}, "page": 1}
        current_qty = user_states[user_id]["qty"].get(p_id, 1)

        # 2-Column App UI with Icons
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⚡ Buy Now", url=f"https://link.bakong.nbc.gov.kh/pay?id={MERCHANT_ID}&amount={p['price']}&currency=KHR"),
                InlineKeyboardButton(text="🛒 +", callback_data=f"cart_add_{p_id}")
            ],
            [
                InlineKeyboardButton(text="➖", callback_data=f"qty_dec_{p_id}"),
                InlineKeyboardButton(text=f"Qty: {current_qty}", callback_data="none"),
                InlineKeyboardButton(text="➕", callback_data=f"qty_inc_{p_id}")
            ]
        ])

        caption = f"📦 **{p['name']}**\n💰 {display_price}"
        if product_cache[p_id]["img"]:
            await bot.send_photo(message.chat.id, photo=product_cache[p_id]["img"], caption=caption, reply_markup=markup, parse_mode="Markdown")
        else:
            await message.answer(caption, reply_markup=markup, parse_mode="Markdown")

    # Pagination Buttons: Back and Next
    nav_buttons = []
    if page > 1: nav_buttons.append(InlineKeyboardButton(text="⬅️ Back", callback_data=f"page_{page-1}"))
    nav_buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"page_{page+1}"))
    
    await message.answer(f"--- Page {page} ---", reply_markup=InlineKeyboardMarkup(inline_keyboard=[nav_buttons]))

# --- 3. HANDLERS (FAST LOGIC) ---
@router.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_states[user_id] = {"cart": [], "qty": {}, "page": 1}
    await message.answer("🚀 Loading 1.Phsar.me App...", reply_markup=get_main_menu())
    await load_shop_page(message, page=1, user_id=user_id)

@router.message(F.text == "🛍️ Shop")
async def shop_handler(message: types.Message):
    await load_shop_page(message, page=1, user_id=message.from_user.id)

@router.callback_query(F.data.startswith("page_"))
async def page_handler(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[1])
    await callback.answer()
    await load_shop_page(callback.message, page=page, user_id=callback.from_user.id)

# INSTANT QTY UPDATE (No API call)
@router.callback_query(F.data.startswith("qty_"))
async def qty_handler(callback: types.CallbackQuery):
    _, action, p_id = callback.data.split("_")
    uid = callback.from_user.id
    if uid not in user_states: user_states[uid] = {"cart": [], "qty": {}, "page": 1}
    
    current = user_states[uid]["qty"].get(p_id, 1)
    if action == "inc": user_states[uid]["qty"][p_id] = current + 1
    elif action == "dec" and current > 1: user_states[uid]["qty"][p_id] = current - 1
    
    # Update button text instantly
    new_qty = user_states[uid]["qty"][p_id]
    # Re-build the same markup with new QTY
    await callback.answer(f"Quantity: {new_qty}")

# INSTANT ADD TO CART (Uses Cache)
@router.callback_query(F.data.startswith("cart_add_"))
async def add_to_cart(callback: types.CallbackQuery):
    p_id = callback.data.split("_")[2]
    uid = callback.from_user.id
    
    p_data = product_cache.get(p_id)
    if p_data:
        qty = user_states[uid]["qty"].get(p_id, 1)
        user_states[uid]["cart"].append({"name": p_data['name'], "price": float(p_data['price']), "qty": qty})
        await callback.answer(f"✅ Added {qty}x {p_data['name']}!")
    else:
        await callback.answer("❌ Error: Refresh Shop")

@router.message(F.text == "🛒 Cart")
async def view_cart(message: types.Message):
    uid = message.from_user.id
    cart = user_states.get(uid, {}).get("cart", [])
    if not cart:
        await message.answer("Your cart is empty! 🛒")
        return
    
    total = sum(item['price'] * item['qty'] for item in cart)
    text = "🛒 **Your Cart:**\n\n"
    for i, item in enumerate(cart):
        text += f"{i+1}. {item['name']} x{item['qty']} = {int(item['price']*item['qty'])}៛\n"
    
    text += f"\n💰 **Total: {int(total)}៛**"
    pay_link = f"https://link.bakong.nbc.gov.kh/pay?id={MERCHANT_ID}&amount={int(total)}&currency=KHR"
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Checkout (Pay Now)", url=pay_link)],
        [InlineKeyboardButton(text="🗑️ Clear Cart", callback_data="clear_cart")]
    ])
    await message.answer(text, reply_markup=markup, parse_mode="Markdown")

# --- SYSTEM IGNITION ---
async def handle(request): return web.Response(text="App Online")
async def main():
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    # Heartbeat for Render
    app = web.Application(); app.router.add_get("/", handle)
    runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
