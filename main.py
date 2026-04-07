import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web
from woocommerce import API

# --- PHSAR.ME CORE ARCHITECTURE ---
API_TOKEN = '8581539352:AAGByoBXhKj26xq2WPZkMdtsIUeYfpaDg6A'
WC_URL = "https://1.phsar.me"
WC_KEY = "ck_6a9c8caa18a2b0ab114ef90bb9e982d69521ec03"
WC_SECRET = "cs_63c256e1b4eba0a65723f054159e55d2148c3c57"

# Update this with your actual ACLEDA/Bakong ID
MERCHANT_ID = "alex@acleda" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

# Initialize WooCommerce Bridge
wcapi = API(
    url=WC_URL,
    consumer_key=WC_KEY,
    consumer_secret=WC_SECRET,
    version="wc/v3",
    timeout=15
)

# --- RENDER HEARTBEAT (Port Binding Security) ---
async def handle(request):
    return web.Response(text="Pizz King x 1.Phsar.me is Online!")

async def start_heartbeat():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Heartbeat Active on Port {port}")

# --- BOT LOGIC (Khmer Priority) ---
@router.message(Command("start"))
async def start_handler(message: types.Message, command: CommandObject):
    # Check if user clicked a "Drama Link" (e.g., ?start=123)
    args = command.args
    if args and args.isdigit():
        await show_product_detail(message, args)
        return

    welcome_msg = (
        "🇰🇭 ស្វាគមន៍មកកាន់ **1.Phsar.me Store**!\n"
        "ទំនិញទាំងអស់ត្រូវបានទាញយកដោយផ្ទាល់ពីវេបសាយ។\n\n"
        "សូមជ្រើសរើសជម្រើសខាងក្រោម៖"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ មើលទំនិញទាំងអស់", callback_data="fetch_all")],
        [InlineKeyboardButton(text="📞 ទំនាក់ទំនងជំនួយ", url="https://t.me/your_contact")]
    ])
    await message.answer(welcome_msg, reply_markup=markup, parse_mode="Markdown")

@router.callback_query(lambda c: c.data == "fetch_all")
async def fetch_all_products(callback: types.CallbackQuery):
    await callback.answer("កំពុងទាញយកទិន្នន័យ...")
    try:
        response = wcapi.get("products", params={"per_page": 10, "status": "publish"})
        products = response.json()
        
        markup = InlineKeyboardMarkup(inline_keyboard=[])
        for p in products:
            markup.inline_keyboard.append([
                InlineKeyboardButton(text=f"📦 {p['name']} - ${p['price']}", callback_data=f"detail_{p['id']}")
            ])
        
        await callback.message.answer("🎯 ជ្រើសរើសទំនិញដែលអ្នកចង់ទិញ៖", reply_markup=markup)
    except Exception as e:
        await callback.message.answer("❌ មានបញ្ហាបច្ចេកទេស។ សូមព្យាយាមម្តងទៀត។")

async def show_product_detail(message, product_id):
    try:
        p = wcapi.get(f"products/{product_id}").json()
        name = p.get('name', 'Unknown Product')
        price = p.get('price', '0.00')
        desc = p.get('short_description', '').replace('<p>', '').replace('</p>', '')
        img_url = p.get('images', [{}])[0].get('src', '')

        pay_link = f"https://link.bakong.nbc.gov.kh/pay?id={MERCHANT_ID}&amount={price}&currency=USD&name=1PhsarMe"
        
        detail_text = f"✨ **{name}**\n\n💰 តម្លៃ: ${price}\n\n{desc}"
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 បង់ប្រាក់តាម ACLEDA (Pay Now)", url=pay_link)],
            [InlineKeyboardButton(text="🔙 ត្រឡប់ក្រោយ", callback_data="fetch_all")]
        ])

        if img_url:
            await bot.send_photo(message.chat.id, photo=img_url, caption=detail_text, reply_markup=markup, parse_mode="Markdown")
        else:
            await message.answer(detail_text, reply_markup=markup, parse_mode="Markdown")
    except:
        await message.answer("❌ មិនអាចស្វែងរកទំនិញនេះឃើញទេ។")

@router.callback_query(lambda c: c.data.startswith('detail_'))
async def detail_callback(callback: types.CallbackQuery):
    product_id = callback.data.split('_')[1]
    await show_product_detail(callback.message, product_id)

# --- SYSTEM IGNITION ---
async def main():
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    await start_heartbeat()
    print("Architect Core: 1.Phsar.me Bridge Ignited!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
