import os
import asyncio
import logging
from datetime import datetime
import pytz
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import WebAppInfo
from aiohttp import web
from woocommerce import API

# --- HARDENED CONFIG ---
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
    await message.answer(f"🇰🇭 <b>ស្វាគមន៍មកកាន់ Pizz King!</b>\nYour ID: <code>{message.from_user.id}</code>", reply_markup=markup, parse_mode="HTML")

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
        
        kh_tz = pytz.timezone('Asia/Phnom_Penh')
        now = datetime.now(kh_tz)
        order_date = now.strftime("%d-%m-%Y")
        order_time = now.strftime("%H:%M")

        # 1. Format High-Visibility Report (HTML SAFE)
        item_list_str = ""
        for i in items:
            item_list_str += f"• {i['name']} x{i['qty']} — {int(i['price'] * i['qty']):,}៛\n"
        
        note_display = f"\n📝 <b>ចំណាំ៖</b> {note}" if note.strip() else "\n📝 <b>ចំណាំ៖</b> គ្មាន"

        report_text = (
            f"🚀 <b>ការកម្ម៉ង់ថ្មី (Mini App)</b>\n"
            f"📅 ថ្ងៃទី: <code>{order_date}</code> | ម៉ោង: <code>{order_time}</code>\n"
            f"👤 ឈ្មោះ: <b>{name}</b>\n"
            f"📞 លេខទូរស័ព្ទ: <code>{phone}</code>\n"
            f"📍 ទីតាំង: <code>{loc}</code>"
            f"{note_display}\n\n"
            f"📦 <b>ទំនិញ៖</b>\n{item_list_str}\n"
            f"💰 <b>សរុប៖ {int(total):,} ៛</b>"
        )

        # 2. SEND TELEGRAM MESSAGES (High Priority)
        # To Group
        try:
            await bot.send_message(GROUP_CHAT_ID, report_text, parse_mode="HTML")
        except Exception as e:
            logging.error(f"Group Send Error: {e}")

        # To Buyer
        if tid:
            try:
                await bot.send_message(tid, f"✅ <b>ការកម្ម៉ង់បានជោគជ័យ!</b>\n\n{report_text}", parse_mode="HTML")
            except Exception as e:
                logging.error(f"Buyer Send Error: {e}")

        # 3. WOOCOMMERCE SYNC (Background)
        try:
            line_items = [{"product_id": int(i['id']), "quantity": i['qty']} for i in items if str(i.get('id', '')).isdigit()]
            wcapi.post("orders", {
                "status": "processing",
                "billing": {"first_name": name, "address_1": loc, "address_2": f"Note: {note}", "phone": phone},
                "line_items": line_items,
                "customer_note": f"{note} (Ordered at {order_date} {order_time})",
                "meta_data": [{"key": "mini_app_note", "value": note}]
            })
        except Exception as e:
            logging.error(f"WC Sync Error: {e}")

        return web.json_response({"status": "success"}, headers=headers)
    except Exception as e:
        logging.error(f"API Endpoint Error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500, headers=headers)

async def main():
    dp.include_router(router)
    app = web.Application()
    app.router.add_get("/", lambda r: web.Response(text="Pizz King Backend Active"))
    app.router.add_post("/create-order", create_order_endpoint)
    app.router.add_options("/create-order", create_order_endpoint)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
