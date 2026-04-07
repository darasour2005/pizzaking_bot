import os
import asyncio
import logging
import json
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiohttp import web
from woocommerce import API

# --- ១. ការកំណត់រចនាសម្ព័ន្ធ (SYSTEM CONFIGURATION) ---
# ព័ត៌មានសម្ងាត់សម្រាប់ហាង 1.phsar.me
API_TOKEN = '8581539352:AAGByoBXhKj26xq2WPZkMdtsIUeYfpaDg6A'
WC_URL = "https://1.phsar.me"
WC_KEY = "ck_6a9c8caa18a2b0ab114ef90bb9e982d69521ec03"
WC_SECRET = "cs_63c256e1b4eba0a65723f054159e55d2148c3c57"
MERCHANT_ID = "alex@acleda"
MY_PHONE = "+85587282827"
MINI_APP_URL = "https://darasour2005.github.io/pizzaking_bot/"

# បង្កើត Bot និង Dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

# ភ្ជាប់ទៅកាន់ WooCommerce API
wcapi = API(
    url=WC_URL,
    consumer_key=WC_KEY,
    consumer_secret=WC_SECRET,
    version="wc/v3",
    timeout=20
)

# --- ២. មុខងារជំនួយ (HELPER FUNCTIONS) ---
def get_main_menu():
    """ បង្កើតប៊ូតុងបញ្ជាផ្នែកខាងក្រោម """
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛍️ បើកហាងទំនិញ", web_app=WebAppInfo(url=MINI_APP_URL))],
        [KeyboardButton(text="🛒 កន្ត្រកទំនិញ"), KeyboardButton(text="📞 ជំនួយ")]
    ], resize_keyboard=True)

# --- ៣. ការគ្រប់គ្រង BOT (BOT HANDLERS) ---
@router.message(Command("start"))
async def start_handler(message: types.Message):
    welcome_text = (
        "🇰🇭 **សូមស្វាគមន៍មកកាន់ Pizz King Store!**\n\n"
        "លោកអ្នកអាចធ្វើការបញ្ជាទិញទំនិញដោយផ្ទាល់តាមរយៈកម្មវិធី Mini App របស់យើង "
        "ដោយចុចប៊ូតុង 'បើកហាងទំនិញ' ខាងក្រោម។"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

@router.message(F.text == "📞 ជំនួយ")
async def help_handler(message: types.Message):
    help_text = (
        f"🙏 **ត្រូវការជំនួយមែនទេ?**\n\n"
        f"សូមទាក់ទងមកយើងខ្ញុំតាមរយៈលេខទូរស័ព្ទ៖\n"
        f"☎️ **{MY_PHONE}**\n\n"
        f"ឬផ្ញើសារមកកាន់ @souralexander"
    )
    await message.answer(help_text, parse_mode="Markdown")

# --- ៤. ការគ្រប់គ្រងការបញ្ជាទិញ (WEB API SERVER) ---
async def handle_heartbeat(request):
    """ រក្សាឱ្យ Render មិនដេក (Keep Render Awake) """
    return web.Response(text="Pizz King Sovereign Server: Active", content_type="text/plain")

async def create_order_endpoint(request):
    """ ទទួលទិន្នន័យពី Mini App និងបង្កើត Order ក្នុង WooCommerce """
    # បន្ថែម CORS Headers ដើម្បីឱ្យ Browser អនុញ្ញាតឱ្យផ្ញើទិន្នន័យ
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    if request.method == "OPTIONS":
        return web.Response(status=200, headers=headers)

    try:
        data = await request.json()
        
        # រៀបចំទិន្នន័យសម្រាប់ WooCommerce
        line_items = []
        for item in data.get('items', []):
            line_items.append({
                "product_id": item['id'],
                "quantity": item['qty']
            })

        order_payload = {
            "payment_method": "bacs",
            "payment_method_title": "Bakong/ACLEDA",
            "set_paid": False,
            "status": "pending",
            "billing": {
                "first_name": "Telegram Customer",
                "address_1": data.get('location', 'No location provided'),
                "phone": data.get('phone', 'No phone provided')
            },
            "line_items": line_items,
            "customer_note": f"Telegram Order via Mini App. Loc: {data.get('location')}"
        }

        # បញ្ជូនទៅកាន់ WordPress/WooCommerce
        result = wcapi.post("orders", order_payload).json()
        order_id = result.get('id')

        # បញ្ជូនសារដំណឹងទៅកាន់ Bot Admin (អ្នកលក់)
        admin_chat_id = "YOUR_PERSONAL_TELEGRAM_ID" # ប្តូរដាក់ ID របស់អ្នកដើម្បីទទួលដំណឹង
        # (Optional) await bot.send_message(admin_chat_id, f"🔔 មានការបញ្ជាទិញថ្មី! ID: {order_id}")

        return web.json_response({"status": "success", "order_id": order_id}, headers=headers)
    
    except Exception as e:
        logging.error(f"Order Error: {str(e)}")
        return web.json_response({"status": "error", "message": str(e)}, status=500, headers=headers)

# --- ៥. ការចាប់ផ្តើមប្រព័ន្ធ (SYSTEM IGNITION) ---
async def main():
    # កំណត់ Logging
    logging.basicConfig(level=logging.INFO)
    
    # បញ្ចូល Router ទៅក្នុង Dispatcher
    dp.include_router(router)
    
    # បង្កើត Web Server (aiohttp)
    app = web.Application()
    app.router.add_get("/", handle_heartbeat)
    app.router.add_post("/create-order", create_order_endpoint)
    app.router.add_options("/create-order", create_order_endpoint) # សម្រាប់ CORS
