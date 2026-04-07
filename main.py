import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web
from woocommerce import API

# --- PIZZ KING & PHSAR.ME ARCHITECTURE ---
API_TOKEN = '8581539352:AAGByoBXhKj26xq2WPZkMdtsIUeYfpaDg6A'
WC_URL = "https://go.phsar.me"
WC_KEY = "ck_bccb08dabb73f264d318c682f90850ce1e39fb30"
WC_SECRET = "cs_2542418b856ad7f3a4915896137d7985dadfef75"

# Your Bakong/ACLEDA ID for payments
MERCHANT_ID = "pizzking@acleda" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

# Initialize WooCommerce Bridge
wcapi = API(
    url=WC_URL,
    consumer_key=WC_KEY,
    consumer_secret=WC_SECRET,
    version="wc/v3",
    timeout=10 # Pulse-Verify: 10s timeout to keep it snappy
)

# --- RENDER HEARTBEAT (Internal Audit: Port Binding) ---
async def handle(request):
    return web.Response(text="Bridge to go.phsar.me is Active!")

async def start_heartbeat():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Render Heartbeat online on port {port}")

# --- BOT COMMANDS (Khmer-Priority) ---
@router.message(Command("start"))
async def start_handler(message: types.Message):
    welcome_msg = (
        "🇰🇭 ស្វាគមន៍មកកាន់ **Pizz King x Phsar.me**!\n"
        "ទំនិញទាំងអស់ត្រូវបានទាញយកដោយផ្ទាល់ពីវេបសាយរបស់យើង។\n\n"
        "សូមចុចប៊ូតុងខាងក្រោមដើម្បីមើលទំនិញថ្មីៗ៖"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ មើលទំនិញទាំងអស់ (View Products)", callback_data="fetch_wc")]
    ])
    await message.answer(welcome_msg, reply_markup=markup, parse_mode="Markdown")

@router.callback_query(lambda c: c.data == "fetch_wc")
async def fetch_products(callback: types.CallbackQuery):
    await callback.answer("កំពុងទាញយកទិន្នន័យ... (Fetching Data)")
    
    try:
        # Fetch top 8 products from WooCommerce
        response = wcapi.get("products", params={"per_page": 8, "status": "publish"})
        products = response.json()
        
        if not products:
            await callback.message.answer("សោកស្តាយ! មិនទាន់មានទំនិញក្នុងហាងនៅឡើយទេ។")
            return

        markup = InlineKeyboardMarkup(inline_keyboard=[])
        
        for p in products:
            # We build a button for each product found on go.phsar.me
            p_id = p['id']
            p_name = p['name']
            p_price = p['price']
            
            markup.inline_keyboard.append([
                InlineKeyboardButton(text=f"📦 {p_name} - ${p_price}", callback_data=f"detail_{p_id}")
            ])
            
        await callback.message.answer("🎯 នេះគឺជាទំនិញដែលមានក្នុងស្តុក៖", reply_markup=markup)
        
    except Exception as e:
        logging.error(f"WooCommerce Error: {e}")
        await callback.message.answer("❌ មានបញ្ហាបច្ចេកទេសក្នុងការភ្ជាប់ទៅកាន់វេបសាយ។")

@router.callback_query(lambda c: c.data.startswith('detail_'))
async def product_detail(callback: types.CallbackQuery):
    p_id = callback.data.split('_')[1]
    p = wcapi.get(f"products/{p_id}").json()
    
    name = p.get('name')
    price = p.get('price')
    desc = p.get('short_description', '').replace('<p>', '').replace('</p>', '')
    
    # Create ACLEDA/Bakong Deep Link
    pay_link = f"https://link.bakong.nbc.gov.kh/pay?id={MERCHANT_ID}&amount={price}&currency=USD&name=PhsarMeStore"
    
    detail_text = f"✨ **{name}**\n\n💰 តម្លៃ: ${price}\n\n{desc}"
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 បង់ប្រាក់តាម ACLEDA (Pay Now)", url=pay_link)],
        [InlineKeyboardButton(text="🔙 ត្រឡប់ក្រោយ", callback_data="fetch_wc")]
    ])
    
    await callback.message.answer(detail_text, reply_markup=markup, parse_mode="Markdown")

# --- SYSTEM IGNITION ---
async def main():
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    
    await start_heartbeat()
    print("Architect Core: Bridge to Phsar.me is Ignite!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
