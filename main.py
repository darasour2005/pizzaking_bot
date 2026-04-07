import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiohttp import web

# --- PIZZ KING CONFIG ---
API_TOKEN = '8581539352:AAGByoBXhKj26xq2WPZkMdtsIUeYfpaDg6A'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- RENDER HEARTBEAT ---
async def handle(request):
    return web.Response(text="Pizz King Bot is Ignite!")

async def start_heartbeat():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render uses the 'PORT' environment variable
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Heartbeat online on port {port}")

# --- BOT COMMANDS ---
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # Khmer-Priority Greeting
    welcome_text = (
        "🍕 ស្វាគមន៍មកកាន់ Pizz King Store!\n"
        "ហាងយើងខ្ញុំមានលក់ផលិតផលប្លែកៗដែលអ្នកចូលចិត្ត។\n\n"
        "ចុច /menu ដើម្បីមើលទំនិញ!"
    )
    await message.reply(welcome_text)

# --- ARCHITECT ENGINE START ---
async def on_startup(dp):
    await start_heartbeat()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
