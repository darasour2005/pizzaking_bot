import os
import asyncio
import logging
import re
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web
from woocommerce import API

# --- ការកំណត់ប្រព័ន្ធ (SYSTEM CONFIG) ---
API_TOKEN = '8581539352:AAGByoBXhKj26xq2WPZkMdtsIUeYfpaDg6A'
WC_URL = "https://1.phsar.me"
WC_KEY = "ck_6a9c8caa18a2b0ab114ef90bb9e982d69521ec03"
WC_SECRET = "cs_63c256e1b4eba0a65723f054159e55d2148c3c57"
MERCHANT_ID = "alex@acleda" 
MY_CONTACT = "https://t.me/+85587282827" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

# ការចងចាំបណ្តោះអាសន្ន (CACHE & SESSION)
product_cache = {} 
user_states = {} # {uid: {"cart": [], "qty": {p_id: 1}}}

wcapi = API(url=WC_URL, consumer_key=WC_KEY, consumer_secret=WC_SECRET, version="wc/v3", timeout=15)

def clean_html(raw_html):
    if not raw_html: return "មិនមានព័ត៌មានលម្អិត"
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

# --- ១. ប៊ូតុងបញ្ជាផ្នែកខាងក្រោម (ONE-LINE APP MENU) ---
def get_main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛍️ ហាងទំនិញ"), KeyboardButton(text="🛒 កន្ត្រកទំនិញ"), KeyboardButton(text="📞 ជំនួយ")]
    ], resize_keyboard=True)

# --- ២. ការបង្កើតប៊ូតុង (INSTANT UI BUILDER) ---
def build_product_markup(p_id, uid):
    qty = user_states[uid]["qty"].get(p_id, 1)
    price = product_cache[p_id]["price"]
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚡ ទិញភ្លាមៗ", url=f"https://link.bakong.nbc.gov.kh/pay?id={MERCHANT_ID}&amount={price}&currency=KHR"),
            InlineKeyboardButton(text="➕ បន្ថែមទៅកន្ត្រក", callback_data=f"cart_add_{p_id}")
        ],
        [
            InlineKeyboardButton(text="➖", callback_data=f"qty_dec_{p_id}"),
            InlineKeyboardButton(text=f"ចំនួន: {qty}", callback_data="none"),
            InlineKeyboardButton(text="➕", callback_data=f"qty_inc_{p_id}")
        ]
    ])

# --- ៣. ការបង្កើតអត្ថបទពិពណ៌នា (CAPTION BUILDER) ---
def build_caption(p_id, uid):
    p = product_cache[p_id]
    cart = user_states[uid]["cart"]
    
    # ព័ត៌មានទំនិញមូលដ្ឋាន
    text = (
        f"🏷️ **{p['name']}**\n"
        f"💰 តម្លៃ: {p['display_price']}\n"
        f"📝 ព័ត៌មានលម្អិត: {p['desc'][:120]}...\n\n"
    )
    
    # បន្ថែមសេចក្តីសង្ខេបកន្ត្រក (CART SUMMARY) - នៅពីលើប៊ូតុង
    if cart:
        total_items = sum(i['qty'] for i in cart)
        total_price = sum(i['price'] * i['qty'] for i in cart)
        text += f"🛒 **កន្ត្រកបច្ចុប្បន្ន: {total_items} មុខ (សរុប {int(total_price)}៛)**"
    else:
        text += "🛒 **កន្ត្រកបច្ចុប្បន្ន: ០ មុខ**"
        
    return text

# --- ៤. បង្ហាញទំនិញ (SHOW PRODUCTS) ---
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
        display_price = f"{p['price']}៛"
        final_price = p['price'] if p['price'] else "0"
        
        if p['on_sale'] and p['sale_price']:
            display_price = f"~~{p['regular_price']}៛~~ 🔥 **{p['sale_price']}៛**"
            final_price = p['sale_price']

        product_cache[p_id] = {
            "name": p['name'],
            "price": final_price,
            "display_price": display_price,
            "img": p['images'][0]['src'] if p['images'] else None,
            "desc": clean_html(p.get('short_description', ''))
        }
        
        if user_id not in user_states: user_states[user_id] = {"cart": [], "qty": {}}
        
        caption = build_caption(p_id, user_id)
        markup = build_product_markup(p_id, user_id)
        
        if product_cache[p_id]["img"]:
            await bot.send_photo(message.chat.id, photo=product_cache[p_id]["img"], caption=caption, reply_markup=markup, parse_mode="Markdown")
        else:
            await message.answer(caption, reply_markup=markup, parse_mode="Markdown")

    nav = [[InlineKeyboardButton(text="⬅️ ថយក្រោយ", callback_data=f"page_{page-1}"), 
            InlineKeyboardButton(text="បន្ទាប់ ➡️", callback_data=f"page_{page+1}")]]
    await message.answer(f"--- ទំព័រទី {page} ---", reply_markup=InlineKeyboardMarkup(inline_keyboard=nav))

# --- ៥. ការបញ្ជា និងការគ្រប់គ្រង (HANDLERS) ---
@router.message(Command("start"))
async def start_handler(message: types.Message):
    user_states[message.from_user.id] = {"cart": [], "qty": {}}
    await message.answer("🚀 **សូមស្វាគមន៍មកកាន់ Pizz King App**", reply_markup=get_main_menu())
    await load_shop_page(message, page=1, user_id=message.from_user.id)

@router.message(F.text == "🛍️ ហាងទំនិញ")
async def shop_handler(message: types.Message):
    await load_shop_page(message, page=1, user_id=message.from_user.id)

@router.callback_query(F.data.startswith("qty_"))
async def qty_handler(callback: types.CallbackQuery):
    _, action, p_id = callback.data.split("_")
    uid = callback.from_user.id
    current = user_states[uid]["qty"].get(p_id, 1)
    
    if action == "inc": user_states[uid]["qty"][p_id] = current + 1
    elif action == "dec" and current > 1: user_states[uid]["qty"][p_id] = current - 1
    
    await callback.message.edit_reply_markup(reply_markup=build_product_markup(p_id, uid))
    await callback.answer()

@router.callback_query(F.data.startswith("cart_add_"))
async def add_to_cart(callback: types.CallbackQuery):
    p_id = callback.data.split("_")[2]
    uid = callback.from_user.id
    p_data = product_cache.get(p_id)
    
    qty = user_states[uid]["qty"].get(p_id, 1)
    user_states[uid]["cart"].append({"name": p_data['name'], "price": float(p_data['price']), "qty": qty})
    
    # ធ្វើបច្ចុប្បន្នភាព Caption ភ្លាមៗ (Cart Summary នឹងលោតឡើងលើប៊ូតុង)
    await callback.message.edit_caption(
        caption=build_caption(p_id, uid), 
        reply_markup=callback.message.reply_markup, 
        parse_mode="Markdown"
    )
    await callback.answer(f"បានបន្ថែម {p_data['name']}")

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

@router.message(F.text == "📞 ជំនួយ")
async def contact_handler(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💬 ផ្ញើសារមកយើង", url=MY_CONTACT)]])
    await message.answer(f"🙏 សម្រាប់ជំនួយ សូមទាក់ទងមកកាន់លេខ: **+85587282827**", reply_markup=markup, parse_mode="Markdown")

@router.callback_query(F.data == "clear_cart")
async def clear_cart_handler(callback: types.CallbackQuery):
    user_states[callback.from_user.id]["cart"] = []
    await callback.message.edit_text("កន្ត្រកទំនិញត្រូវបានលុបចោល។ 🛍️")

@router.callback_query(F.data.startswith("page_"))
async def page_handler(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[1])
    await callback.answer()
    await load_shop_page(callback.message, page=page, user_id=callback.from_user.id)

# --- SYSTEM IGNITION ---
async def handle(request): return web.Response(text="Pizz King Online")
async def main():
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    app = web.Application(); app.router.add_get("/", handle)
    runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
