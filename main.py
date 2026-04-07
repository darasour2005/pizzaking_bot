import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiohttp import web # This is the "Heartbeat" for Render

# --- CONFIG ---
API_TOKEN = '8581539352:AAGByoBXhKj26xq2WPZkMdtsIUeYfpaDg6A'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- DUMMY WEB SERVER FOR RENDER ---
async def handle(request):
    return web.Response(text="Pizz King Bot is Alive!")

app = web.Application()
app.router.add_get("/", handle)

# --- BOT LOGIC ---
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("ស្វាគមន៍មកកាន់ Pizz King Store! 🍕")

# --- MULTI-PASS AUDIT START ---
async def on_startup(dp):
    # This starts the web server in the background
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()
    print("Architect Core: Heartbeat Server Started on Port", os.environ.get("PORT", 10000))

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
