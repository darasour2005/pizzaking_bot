import os
import asyncio
import logging
import json
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiohttp import web
from woocommerce import API

# --- CONFIG ---
API_TOKEN = '8581539352:AAGByoBXhKj26xq2WPZkMdtsIUeYfpaDg6A'
WC_URL = "https://1.phsar.me"
WC_KEY = "ck_6a9c8caa18a2b0ab114ef90bb9e982d69521ec03"
WC_SECRET = "cs_63c256e1b4eba0a65723f054159e55d2148c3c57"
MY_PHONE = "+85587282827"
MINI_APP_URL = "https://darasour2005.github.io/pizzaking_bot/"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()
wcapi = API(url=WC_URL, consumer_key=WC_KEY, consumer_secret=WC_SECRET, version="wc/v3", timeout=20)

# --- BOT ---
@router.message(Command("start"))
async def start_handler(message: types.Message):
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🛍️ បើកហាងទំនិញ", web_app=WebAppInfo(url=MINI_APP_URL))]], resize_keyboard=True)
    await message.answer("🇰🇭 **ស្វាគមន៍មកកាន់ Pizz King!**", reply_markup=markup, parse_mode="Markdown")

# --- ORDER API ---
async def create_order_endpoint(request):
    headers = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type"}
    if request.method == "OPTIONS": return web.Response(status=200, headers=headers)
    try:
        data = await request.json()
        tid, name, phone, loc, items, total = data.get('telegram_id'), data.get('name'), data.get('phone'), data.get('location'), data.get('items'), data.get('total')
        
        # WooCommerce Save
        line_items = [{"product_id": i['id'], "quantity": i['qty']} for i in items]
        wcapi.post("orders", {
            "billing": {"first_name": name, "address_1": loc, "phone": phone},
            "line_items": line_items,
            "customer_note": f"TG ID: {tid} | Name: {name}"
        })

        # Send Receipt from @pizzaking_bot
        if tid:
            receipt = f"✅ **ការកម្ម៉ង់ជោគជ័យ!**\n\n👤 ឈ្មោះ: {name}\n📞 លេខទូរស័ព្ទ: {phone}\n📍 ទីតាំង: {loc}\n\n📦 **ទំនិញ:**\n"
            for i in items: receipt += f"• {i['name']} x{i['qty']} = {int(i['price']*i['qty']).toLocaleString()}៛\n"
            receipt += f"\n💰 **សរុប: {int(total).toLocaleString()}៛**\n\n🙏 បន្ទាប់ពីបង់ប្រាក់ សូមផ្ញើ Screenshot មកកាន់ពួកយើង!"
            await bot.send_message(tid, receipt, parse_mode="Markdown")

        return web.json_response({"status": "success"}, headers=headers)
    except Exception as e: return web.json_response({"status": "error", "message": str(e)}, status=500, headers=headers)

# --- IGNITION ---
async def main():
    dp.include_router(router)
    app = web.Application()
    app.router.add_get("/", lambda r: web.Response(text="Active"))
    app.router.add_post("/create-order", create_order_endpoint)
    app.router.add_options("/create-order", create_order_endpoint)
    runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
