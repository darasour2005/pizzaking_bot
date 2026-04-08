import os
import asyncio
import logging
from datetime import datetime
try:
    import pytz
except ImportError:
    os.system('pip install pytz')
    import pytz

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import WebAppInfo
from aiohttp import web
from woocommerce import API

# --- CONFIG ---
API_TOKEN = '8503376154:AAGsDQEaLHCq3E_ttoCAT46SygrD2VubP-E' 
WC_URL = "https://1.phsar.me"
WC_KEY = "ck_6a9c8caa18a2b0ab114ef90bb9e982d69521ec03"
WC_SECRET = "cs_63c256e1b4eba0a65723f054159e55d2148c3c57"
MINI_APP_URL = "https://darasour2005.github.io/pizzaking_bot/"
GROUP_CHAT_ID = '-1003499575831' 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()
wcapi = API(url=WC_URL, consumer_key=WC_KEY, consumer_secret=WC_SECRET, version="wc/v3", timeout=15)

@router.message(Command("start"))
async def start_handler(message: types.Message):
    markup = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="🛍️ បើកហាងទំនិញ", web_app=WebAppInfo(url=MINI_APP_URL))]], 
        resize_keyboard=True
    )
    await message.answer("🇰🇭 **ស្វាគមន៍មកកាន់ Pizz King!**", reply_markup=markup, parse_mode="Markdown")

async def create_order_endpoint(request):
    headers = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type"}
    if request.method == "OPTIONS": return web.Response(status=200, headers=headers)
        
    try:
        data = await request.json()
        tid = data.get('telegram_id')
        name = data.get('name', 'N/A')
        phone = data.get('phone', 'N/A')
        loc = data.get('location', 'N/A')
        note = data.get('note', '')
        items = data.get('items', [])
        total = data.get('total', 0)
        
        # TIMESTAMP ENGINE (Asia/Phnom_Penh)
        kh_tz = pytz.timezone('Asia/Phnom_Penh')
        now = datetime.now(kh_tz)
        order_date = now.strftime("%d-%m-%Y")
        order_time = now.strftime("%H:%M")

        # 1. Format Telegram Report (Create this FIRST)
        item_list_str = "".join([f"• {i['name']} x{i['qty']} — {int(i['price'] * i['qty']):,}៛\n" for i in items])
        note_display = f"\n📝 **ចំណាំ៖** {note}" if note.strip() else ""

        report_text = (
            f"🚀 **ការកម្ម៉ង់ថ្មី (Mini App)**\n"
            f"📅 ថ្ងៃទី: `{order_date}` | ម៉ោង: `{order_time}`\n"
            f"👤 ឈ្មោះ: **{name}**\n"
            f"📞 លេខទូរស័ព្ទ: `{phone}`\n"
            f"📍 ទីតាំង: `{loc}`"
            f"{note_display}\n\n"
            f"📦 **ទំនិញ៖**\n{item_list_str}\n"
            f"💰 **សរុប៖ {int(total):,} ៛**"
        )

        # 2. SEND TELEGRAM MESSAGES (High Priority - Do this before WooCommerce)
        # Send to Admin Group
        try:
            await bot.send_message(GROUP_CHAT_ID, report_text, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Group Notify Error: {e}")

        # Send to Buyer
        if tid:
            try:
                await bot.send_message(tid, f"✅ **ការកម្ម៉ង់បានជោគជ័យ!**\n\n{report_text}", parse_mode="Markdown")
            except Exception as e:
                logging.error(f"Buyer Notify Error: {e}")

        # 3. WOOCOMMERCE SYNC (Lower Priority - Silent failure guard)
        try:
            line_items = []
            for i in items:
                item_id = str(i.get('id', ''))
                if item_id.isdigit():
                    line_items.append({"product_id": int(item_id), "quantity": i['qty']})
            
            wcapi.post("orders", {
                "status": "processing",
                "billing": {"first_name": name, "address_1": loc, "phone": phone},
                "line_items": line_items,
                "customer_note": f"Note: {note} | Phone: {phone} | Time: {order_date} {order_time}"
            })
        except Exception as e:
            logging.error(f"WooCommerce Sync Error (Non-Fatal): {e}")

        return web.json_response({"status": "success"}, headers=headers)
    except Exception as e:
        logging.error(f"Global Error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500, headers=headers)

async def main():
    dp.include_router(router)
    app = web.Application()
    app.router.add_post("/create-order", create_order_endpoint)
    app.router.add_options("/create-order", create_order_endpoint)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
