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
API_TOKEN = '8581539352:AAGByoBXhKj26xq2WPZkMdtsIUeYfpaDg6A'
WC_URL = "https://1.phsar.me"
WC_KEY = "ck_6a9c8caa18a2b0ab114ef90bb9e982d69521ec03"
WC_SECRET = "cs_63c256e1b4eba0a65723f054159e55d2148c3c57"
MERCHANT_ID = "alex@acleda"
MY_PHONE = "+85587282827"
MINI_APP_URL = "https://darasour2005.github.io/pizzaking_bot/"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

wcapi = API(
    url=WC_URL,
    consumer_key=WC_KEY,
    consumer_secret=WC_SECRET,
    version="wc/v3",
    timeout=20
)

# --- ២. មុខងារជំនួយ (HELPER FUNCTIONS) ---
def get_main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛍️ បើកហាងទំនិញ", web_app=WebAppInfo(url=MINI_APP_URL))],
        [KeyboardButton(text="🛒 កន្ត្រកទំនិញ"), KeyboardButton(text="📞 ជំនួយ")]
    ], resize_keyboard=True)

# --- ៣. ការគ្រប់គ្រង BOT (BOT HANDLERS) ---
@router.message(Command("start"))
async def start_handler(message: types.Message):
    welcome_text = (
        "🇰🇭 **សូមស្វាគមន៍មកកាន់ Pizz King Store!**\n\n"
        "ចុចប៊ូតុង 'បើកហាងទំនិញ' ខាងក្រោមដើម្បីបញ្ជាទិញទំនិញដែលអ្នកចង់បាន។"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

@router.message(F.text == "📞 ជំនួយ")
async def help_handler(message: types.Message):
    await message.answer(f"🙏 សម្រាប់ជំនួយ សូមទាក់ទងមកកាន់លេខ៖\n☎️ **{MY_PHONE}**", parse_mode="Markdown")

# --- ៤. ការគ្រប់គ្រងការបញ្ជាទិញ និងផ្ញើវិក្កយបត្រ (ORDER & RECEIPT LOGIC) ---
async def handle_heartbeat(request):
    return web.Response(text="Pizz King Server is Active", content_type="text/plain")

async def create_order_endpoint(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    if request.method == "OPTIONS":
        return web.Response(status=200, headers=headers)

    try:
        data = await request.json()
        telegram_id = data.get('telegram_id')
        
        # ១. រៀបចំទិន្នន័យសម្រាប់ WooCommerce
        line_items = [{"product_id": i['id'], "quantity": i['qty']} for i in data['items']]
        order_payload = {
            "payment_method": "bacs",
            "payment_method_title": "Bakong/ACLEDA",
            "set_paid": False,
            "billing": {
                "address_1": data.get('location'),
                "phone": data.get('phone')
            },
            "line_items": line_items,
            "customer_note": f"Order from Telegram Mini App. Phone: {data.get('phone')}"
        }

        # ២. បង្កើត Order ក្នុង WooCommerce
        result = wcapi.post("orders", order_payload).json()
        order_id = result.get('id')

        # ៣. ផ្ញើវិក្កយបត្រទៅកាន់អ្នកទិញ (SEND RECEIPT TO BUYER)
        if telegram_id:
            receipt_text = (
                f"✅ **ការបញ្ជាទិញទទួលបានជោគជ័យ!**\n\n"
                f"🆔 លេខវិក្កយបត្រ: #{order_id}\n"
                f"📍 ទីតាំង: {data.get('location')}\n"
                f"📞 លេខទូរស័ព្ទ: {data.get('phone')}\n\n"
                f"📦 **ទំនិញដែលបានកម្ម៉ង់:**\n"
            )
            for item in data['items']:
                receipt_text += f"• {item['name']} x{item['qty']}\n"
            
            receipt_text += f"\n💰 **សរុបដែលត្រូវបង់: {int(data['total'])}៛**\n\n"
            receipt_text += "🙏 អរគុណសម្រាប់ការគាំទ្រ! យើងនឹងទាក់ទងទៅលោកអ្នកក្នុងពេលឆាប់ៗនេះ។"
            
            await bot.send_message(telegram_id, receipt_text, parse_mode="Markdown")

        return web.json_response({"status": "success", "order_id": order_id}, headers=headers)
    
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return web.json_response({"status": "error", "message": str(e)}, status=500, headers=headers)

# --- ៥. ការចាប់ផ្តើមប្រព័ន្ធ (SYSTEM IGNITION) ---
async def main():
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    
    app = web.Application()
    app.router.add_get("/", handle_heartbeat)
    app.router.add_post("/create-order", create_order_endpoint)
    app.router.add_options("/create-order", create_order_endpoint)

    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    print("Architect Core Online. Sovereign Engine Ready.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
