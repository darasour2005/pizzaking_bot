import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web
from woocommerce import API

# --- PHSAR.ME SMART APP CONFIG ---
API_TOKEN = '8581539352:AAGByoBXhKj26xq2WPZkMdtsIUeYfpaDg6A'
WC_URL = "https://1.phsar.me"
WC_KEY = "ck_6a9c8caa18a2b0ab114ef90bb9e982d69521ec03"
WC_SECRET = "cs_63c256e1b4eba0a65723f054159e55d2148c3c57"
MERCHANT_ID = "alex@acleda" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

# CACHE & STATE
product_cache = {}
user_states = {} # {uid: {"cart": [], "qty": {p_id: 1}, "page": 1}}

wcapi = API(url=WC_URL, consumer_key=WC_KEY, consumer_secret=WC_SECRET, version="wc/v3", timeout=10)

def get_main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛍️ Shop"), KeyboardButton(text="🛒 Cart"), KeyboardButton(text="📞 Help")]
    ], resize_keyboard=True)

# --- SMART UI BUILDER ---
def build_product_markup(p_id, uid):
    qty = user_states[uid]["qty"].get(p_id, 1)
    price = product_cache[p_id]["price"]
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚡ Buy Now", url=f"https://link.bakong.nbc.gov.kh/pay?id={MERCHANT_ID}&amount={price}&currency=KHR"),
            InlineKeyboardButton(text="🛒 + Add", callback_data=f"cart_add_{p_id}")
        ],
        [
            InlineKeyboardButton(text="➖", callback_data=f"qty_dec_{p_id}"),
            InlineKeyboardButton(text=f"Qty: {qty}", callback_data="none"),
            InlineKeyboardButton(text="➕", callback_data=f"qty_inc_{p_id}")
        ]
    ])

async def load_shop_page(message, page=1, user_id=None):
    try:
        products = wcapi.get("products", params={"per_page": 6, "page": page, "status": "publish"}).json()
    except:
        await message.answer("⚠️ Connection Error.")
        return

    for p in products:
        p_id = str(p['id'])
        product_cache[p_id] = {
            "name": p['name'],
            "price": p['price'] if p['price'] else "0",
            "img": p['images'][0]['src'] if p['images'] else None
        }
        
        if user_id not in user_states: user_states[user_id] = {"cart": [], "qty": {}, "page": 1}
        
        caption = f"📦 **{p['name']}**\n💰 Price: **{p['price']}៛**"
        markup = build_product_markup(p_id, user_id)
        
        if product_cache[p_id]["img"]:
            await bot.send_photo(message.chat.id, photo=product_cache[p_id]["img"], caption=caption, reply_markup=markup, parse_mode="Markdown")
        else:
            await message.answer(caption, reply_markup=markup, parse_mode="Markdown")

    nav = [[InlineKeyboardButton(text="⬅️ Back", callback_data=f"page_{page-1}"), InlineKeyboardButton(text="Next ➡️", callback_data=f"page_{page+1}")]]
    await message.answer(f"--- Page {page} ---", reply_markup=InlineKeyboardMarkup(inline_keyboard=nav))

# --- SMART HANDLERS ---
@router.message(Command("start"))
async def start_handler(message: types.Message):
    user_states[message.from_user.id] = {"cart": [], "qty": {}, "page": 1}
    await message.answer("🚀 **Welcome to 1.Phsar.me App**", reply_markup=get_main_menu())
    await load_shop_page(message, page=1, user_id=message.from_user.id)

# UPDATE QTY INSTANTLY
@router.callback_query(F.data.startswith("qty_"))
async def qty_handler(callback: types.CallbackQuery):
    _, action, p_id = callback.data.split("_")
    uid = callback.from_user.id
    
    current = user_states[uid]["qty"].get(p_id, 1)
    if action == "inc": user_states[uid]["qty"][p_id] = current + 1
    elif action == "dec" and current > 1: user_states[uid]["qty"][p_id] = current - 1
    
    # Update the buttons without flickering
    await callback.message.edit_reply_markup(reply_markup=build_product_markup(p_id, uid))
    await callback.answer()

# SMART CART COUNTER
@router.callback_query(F.data.startswith("cart_add_"))
async def add_to_cart(callback: types.CallbackQuery):
    p_id = callback.data.split("_")[2]
    uid = callback.from_user.id
    
    p_data = product_cache.get(p_id)
    qty = user_states[uid]["qty"].get(p_id, 1)
    user_states[uid]["cart"].append({"name": p_data['name'], "price": float(p_data['price']), "qty": qty})
    
    # Calculate New Totals
    cart = user_states[uid]["cart"]
    total_items = sum(i['qty'] for i in cart)
    total_price = sum(i['price'] * i['qty'] for i in cart)
    
    # Update the caption to show current cart status
    new_caption = (
        f"📦 **{p_data['name']}**\n"
        f"💰 Price: **{p_data['price']}៛**\n"
        f"✅ Added {qty} to cart!\n\n"
        f"🛒 **Your Cart: {total_items} items ({int(total_price)}៛)**"
    )
    
    try:
        await callback.message.edit_caption(caption=new_caption, reply_markup=callback.message.reply_markup, parse_mode="Markdown")
    except:
        await callback.message.edit_text(new_caption, reply_markup=callback.message.reply_markup, parse_mode="Markdown")
    
    await callback.answer(f"Added {qty}x {p_data['name']}")

@router.message(F.text == "🛒 Cart")
async def view_cart(message: types.Message):
    uid = message.from_user.id
    cart = user_states.get(uid, {}).get("cart", [])
    if not cart:
        await message.answer("Your cart is empty! 🛒")
        return
    
    total = sum(item['price'] * item['qty'] for item in cart)
    text = "🛒 **Current Order Summary:**\n\n"
    for item in cart:
        text += f"• {item['name']} x{item['qty']} = {int(item['price']*item['qty'])}៛\n"
    
    text += f"\n💰 **Total to Pay: {int(total)}៛**"
    pay_link = f"https://link.bakong.nbc.gov.kh/pay?id={MERCHANT_ID}&amount={int(total)}&currency=KHR"
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Pay Now with ACLEDA", url=pay_link)],
        [InlineKeyboardButton(text="🗑️ Clear Cart", callback_data="clear_cart")]
    ])
    await message.answer(text, reply_markup=markup, parse_mode="Markdown")

@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: types.CallbackQuery):
    user_states[callback.from_user.id]["cart"] = []
    await callback.message.edit_text("Cart Cleared! 🛍️")

# --- SYSTEM IGNITION ---
async def handle(request): return web.Response(text="Pizz King App Online")
async def main():
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    app = web.Application(); app.router.add_get("/", handle)
    runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
