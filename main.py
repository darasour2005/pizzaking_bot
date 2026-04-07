import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web
from woocommerce import API

# --- PHSAR.ME SOVEREIGN CONFIG ---
API_TOKEN = '8581539352:AAGByoBXhKj26xq2WPZkMdtsIUeYfpaDg6A'
WC_URL = "https://1.phsar.me"
WC_KEY = "ck_6a9c8caa18a2b0ab114ef90bb9e982d69521ec03"
WC_SECRET = "cs_63c256e1b4eba0a65723f054159e55d2148c3c57"
MERCHANT_ID = "alex@acleda" 
MY_CONTACT = "https://t.me/+85587282827" # Your direct Telegram link

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

# CACHE & SESSION (Pulse-Verify: Use local memory for instant speed)
product_cache = {} 
user_states = {} # {uid: {"cart": [], "qty": {p_id: 1}, "page": 1}}

wcapi = API(url=WC_URL, consumer_key=WC_KEY, consumer_secret=WC_SECRET, version="wc/v3", timeout=15)

# --- 1. KHMER APP MENU ---
def get_main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛍️ ហាងទំនិញ"), KeyboardButton(text="🛒 កន្ត្រកទំនិញ")],
        [KeyboardButton(text="📞 ជំនួយ & ទំនាក់ទំនង")]
    ], resize_keyboard=True)

# --- 2. SMART UI BUILDER (Instant Update Logic) ---
def build_product_markup(p_id, uid):
    # Retrieve current local QTY without asking WordPress
    qty = user_states[uid]["qty"].get(p_id, 1)
    price = product_cache[p_id]["price"]
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚡ ទិញភ្លាមៗ", url=f"https://link.bakong.nbc.gov.kh/pay?id={MERCHANT_ID}&amount={price}&currency=KHR"),
            InlineKeyboardButton(text="➕ បន្ថែម", callback_data=f"cart_add_{p_id}")
        ],
        [
            InlineKeyboardButton(text="➖", callback_data=f"qty_dec_{p_id}"),
            InlineKeyboardButton(text=f"ចំនួន: {qty}", callback_data="none"),
            InlineKeyboardButton(text="➕", callback_data=f"qty_inc_{p_id}")
        ]
    ])

async def load_shop_page(message, page=1, user_id=None):
    loading_msg = await message.answer("📦 **កំពុងទាញយកទំនិញ... សូមរង់ចាំបន្តិច**")
    
    try:
        products = wcapi.get("products", params={"per_page": 6, "page": page, "status": "publish"}).json()
    except:
        await loading_msg.edit_text("⚠️ បញ្ហាក្នុងការភ្ជាប់ទៅកាន់វេបសាយ។")
        return

    await loading_msg.delete()

    for p in products:
        p_id = str(p['id'])
        
        # VARIATION LOGIC: Show price range if variable
        if p['type'] == 'variable':
            price_display = f"{p['min_price']}៛ - {p['max_price']}៛"
            final_price = p['min_price']
        else:
            price_display = f"{p['price']}៛"
            final_price = p['price']

        # Sale logic
        if p['on_sale'] and p['sale_price']:
            price_display = f"~~{p['regular_price']}៛~~ 🔥 **{p['sale_price']}៛**"
            final_price = p['sale_price']

        product_cache[p_id] = {
            "name": p['name'],
            "price": final_price if final_price else "0",
            "img": p['images'][0]['src'] if p['images'] else None
        }
        
        if user_id not in user_states: user_states[user_id] = {"cart": [], "qty": {}, "page": 1}
        
        caption = f"🏷️ **{p['name']}**\n💰 តម្លៃ: **{price_display}**"
        markup = build_product_markup(p_id, user_id)
        
        if product_cache[p_id]["img"]:
            await bot.send_photo(message.chat.id, photo=product_cache[p_id]["img"], caption=caption, reply_markup=markup, parse_mode="Markdown")
        else:
            await message.answer(caption, reply_markup=markup, parse_mode="Markdown")

    # Pagination
    nav = [[InlineKeyboardButton(text="⬅️ ថយក្រោយ", callback_data=f"page_{page-1}"), 
            InlineKeyboardButton(text="បន្ទាប់ ➡️", callback_data=f"page_{page+1}")]]
    await message.answer(f"--- ទំព័រទី {page} ---", reply_markup=InlineKeyboardMarkup(inline_keyboard=nav))

# --- 3. ZERO-LATENCY HANDLERS ---
@router.message(Command("start"))
async def start_handler(message: types.Message):
    user_states[message.from_user.id] = {"cart": [], "qty": {}, "page": 1}
    await message.answer("🚀 **សូមស្វាគមន៍មកកាន់ Pizz King App**", reply_markup=get_main_menu())
    await load_shop_page(message, page=1, user_id=message.from_user.id)

@router.callback_query(F.data.startswith("qty_"))
async def qty_handler(callback: types.CallbackQuery):
    _, action, p_id = callback.data.split("_")
    uid = callback.from_user.id
    
    # Instant Update in Memory
    current = user_states[uid]["qty"].get(p_id, 1)
    if action == "inc": user_states[uid]["qty"][p_id] = current + 1
    elif action == "dec" and current > 1: user_states[uid]["qty"][p_id] = current - 1
    
    # Update buttons INSTANTLY on screen
    try:
        await callback.message.edit_reply_markup(reply_markup=build_product_markup(p_id, uid))
        await callback.answer() # Removes the loading spinner on the button
    except:
        await callback.answer()

@router.callback_query(F.data.startswith("cart_add_"))
async def add_to_cart(callback: types.CallbackQuery):
    p_id = callback.data.split("_")[2]
    uid = callback.from_user.id
    p_data = product_cache.get(p_id)
    
    qty = user_states[uid]["qty"].get(p_id, 1)
    user_states[uid]["cart"].append({"name": p_data['name'], "price": float(p_data['price']), "qty": qty})
    
    # Calculate New Totals for the "Power Cart"
    cart = user_states[uid]["cart"]
    total_items = sum(i['qty'] for i in cart)
    total_price = sum(i['price'] * i['qty'] for i in cart)
    
    # SMART UPDATE: Update the caption to show the Cart Counter
    new_caption = (
        f"🏷️ **{p_data['name']}**\n"
        f"💰 តម្លៃ: **{p_data['price']}៛**\n"
        f"✅ បានបន្ថែម {qty} ទៅក្នុងកន្ត្រក!\n\n"
        f"🛒 **កន្ត្រកបច្ចុប្បន្ន: {total_items} មុខ (សរុប {int(total_price)}៛)**"
    )
    
    try:
        await callback.message.edit_caption(caption=new_caption, reply_markup=callback.message.reply_markup, parse_mode="Markdown")
    except:
        pass
    
    await callback.answer(f"បូកបញ្ចូល {qty} {p_data['name']}")

@router.message(F.text == "🛒 កន្ត្រកទំនិញ")
async def view_cart(message: types.Message):
    uid = message.from_user.id
    cart = user_states.get(uid, {}).get("cart", [])
    if not cart:
        await message.answer("កន្ត្រកទំនិញរបស់អ្នកគឺទទេ! 🛒")
        return
    
    total = sum(item['price'] * item['qty'] for item in cart)
    text = "🛒 **សេចក្តីសង្ខេបនៃការបញ្ជាទិញ:**\n\n"
    for item in cart:
        text += f"• {item['name']} x{item['qty']} = {int(item['price']*item['qty'])}៛\n"
    
    text += f"\n💰 **សរុបដែលត្រូវបង់: {int(total)}៛**"
    pay_link = f"https://link.bakong.nbc.gov.kh/pay?id={MERCHANT_ID}&amount={int(total)}&currency=KHR"
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 បង់ប្រាក់ឥឡូវនេះ (ACLEDA/Bakong)", url=pay_link)],
        [InlineKeyboardButton(text="🗑️ លុបកន្ត្រក", callback_data="clear_cart")]
    ])
    await message.answer(text, reply_markup=markup, parse_mode="Markdown")

@router.message(F.text == "📞 ជំនួយ & ទំនាក់ទំនង")
async def contact_handler(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 ផ្ញើសារមកកាន់យើង", url=MY_CONTACT)]
    ])
    await message.answer(f"🙏 សម្រាប់ព័ត៌មានបន្ថែម ឬជំនួយបច្ចេកទេស សូមទាក់ទងមកកាន់លេខ: **+85587282827**", reply_markup=markup, parse_mode="Markdown")

# --- SYSTEM IGNITION ---
async def handle(request): return web.Response(text="Pizz King Ignite")
async def main():
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    app = web.Application(); app.router.add_get("/", handle)
    runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
