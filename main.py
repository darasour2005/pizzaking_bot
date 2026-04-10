# main.py - MASTER DISPATCHER V3.0
import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo
from aiohttp import web

import config
import woo_handler  # Your specialized order logic
import video_streamer # The new MTProto streaming engine
import ai_handler  # Import the new AI handler at the top of your main file

# Bot Setup
bot = Bot(token=config.TELEGRAM_API_TOKEN)
dp = Dispatcher()
router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    markup = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="🛍️ បើកហាងទំនិញ", web_app=WebAppInfo(url=config.MINI_APP_URL))]], 
        resize_keyboard=True
    )
    await message.answer(f"🇰🇭 <b>Pizz King Streamer Engine</b>\nYour ID: <code>{message.from_user.id}</code>", reply_markup=markup, parse_mode="HTML")

async def main():
    dp.include_router(router)
    app = web.Application()

   
    # Add the AI routes to your aiohttp application setup
    # (Look for where you define app = web.Application() and add these right below it)
    app.router.add_post('/ai-chat', ai_handler.process_chat_endpoint)
    app.router.add_options('/ai-chat', ai_handler.process_chat_endpoint) # Required for CORS
    
    # 🔗 Routing Table
    app.router.add_get("/", lambda r: web.Response(text="Pizz King System V3.0 Online"))
    
    # Order Logic (Preserving Zero Omission from V1.0)
    app.router.add_post("/create-order", woo_handler.create_order_endpoint)
    app.router.add_options("/create-order", woo_handler.create_order_endpoint)
    
    # Video Streaming Logic (The MTProto Bridge)
    app.router.add_get("/stream/{message_id}", video_streamer.stream_movie_endpoint)

    # 🚀 STARTUP SEQUENCE
    # Start MTProto Client first to ensure it's ready for requests
    await video_streamer.stream_client.start()

    # Start Server on Render's assigned Port
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()
    
    logging.info("System V3.0 Dispatcher Started Successfully")
    
    # Start Polling and handle clean shutdown
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await video_streamer.stream_client.stop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
