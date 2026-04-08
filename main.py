import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo
from aiohttp import web
from woocommerce import API

# --- CONFIG ---
# YOUR HARDENED BOT TOKEN
API_TOKEN = '8503376154:AAGsDQEaLHCq3E_ttoCAT46SygrD2VubP-E' 

WC_URL = "https://1.phsar.me"
WC_KEY = "ck_6a9c8caa18a2b0ab114ef90bb9e982d69521ec03"
WC_SECRET = "cs_63c256e1b4eba0a65723f054159e55d2148c3c57"
MINI_APP_URL = "https://darasour2005.github.io/pizzaking_bot/"

# YOUR SPECIFIC GROUP CHAT ID
GROUP_CHAT_ID = '-1003499575831' 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()
wcapi = API(url=WC_URL, consumer_key=WC_KEY, consumer_secret=WC_SECRET, version="wc/v3", timeout=20)

# --- BOT HANDLERS ---
@router.message(Command("start"))
async def start_handler(message: types.Message):
    markup = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="🛍️ បើកហាងទំនិញ", web_app=WebAppInfo(url=MINI_APP_URL))]], 
        resize_keyboard=True
    )
    await message.answer("🇰🇭 **ស្វាគមន៍មកកាន់ Pizz King!**\nសូមចុចប៊ូតុងខាងក្រោមដើម្បីចូលមើលទំនិញ និងកម្ម៉ង់។", reply_markup=markup, parse_mode="Markdown")

# --- ORDER API ENDPOINT ---
async def create_order_endpoint(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    
    if request.method == "OPTIONS": 
        return web.Response(status=200, headers=headers)
        
    try:
        data = await request.json()
        tid = data.get('telegram_id')
        name = data.get('name', 'N/A')
        phone = data.get('phone', 'N/A') # CAPTURING PHONE
        loc = data.get('location', 'N/A')
        items = data.get('items', [])
        total = data.get('total', 0)
        
        # 1. WooCommerce Sync Protocol (Hardened)
        line_items = []
        for i in items:
            item_id = str(i.get('id', ''))
            if item_id.isdigit():
                line_items.append({"product_id": int(item_id), "quantity": i['qty']})
        
        # We send all data to WC so it appears correctly in your WP Admin panel
        wcapi.post("orders", {
            "status": "processing",
            "billing": {
                "first_name": name, 
                "address_1": loc, 
                "phone": phone  # SYNC PHONE TO WC
            },
            "line_items": line_items,
            "customer_note": f"MiniApp Order | Phone: {phone} | Loc: {loc}"
        })

        # 2. Format High-Visibility Report (Zero-Omission)
        item_list_str = ""
        for i in items:
            item_list_str += f"• {i['name']} x{i['qty']} — {int(i['price'] * i['qty']):,}៛\n"

        report_text = (
            f"👤 ឈ្មោះ: **{name}**\n"
            f"📞 លេខទូរស័ព្ទ: `{phone}`\n"
            f"📍 ទីតាំង: `{loc}`\n\n"
            f"📦 **ទំនិញ៖**\n{item_list_str}\n"
            f"💰 **សរុប៖ {int(total):,} ៛**"
        )

        # 3. Notification: Send to Customer (Receipt)
        if tid:
            try:
                # Adding Greeting and Order ID Context
                await bot.send_message(tid, f"✅ **ការកម្ម៉ង់បានជោគជ័យ!**\n\n{report_text}\n\n🙏 សូមអរគុណសម្រាប់ការកម្ម៉ង់!", parse_mode="Markdown")
            except Exception as e:
                logging.error(f"User Receipt Failure: {e}")

        # 4. Notification: Send Copy to Admin Group (@Mulberrysrbot)
        try:
            await bot.send_message(GROUP_CHAT_ID, f"🚀 **ការកម្ម៉ង់ថ្មី (Mini App)**\n\n{report_text}", parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Group Copy Failure: {e}")

        return web.json_response({"status": "success"}, headers=headers)
        
    except Exception as e:
        logging.error(f"Global Endpoint Error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500, headers=headers)

async def main():
    dp.include_router(router)
    app = web.Application()
    app.router.add_get("/", lambda r: web.Response(text="Pizz King Backend is Live"))
    app.router.add_post("/create-order", create_order_endpoint)
    app.router.add_options("/create-order", create_order_endpoint)
    
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
