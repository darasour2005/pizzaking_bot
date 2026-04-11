# main.py - MASTER DISPATCHER V3.1
# Zero-Omission: Triple-Model AI + Secure Proxy + Streaming Sync

import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo
from aiohttp import web

import config
import woo_handler      # Final autonomous order hub
import video_streamer   # MTProto streaming engine
import ai_handler       # Dual AI Orchestrator with memory

# 1. BOT ARCHITECTURE
bot = Bot(token=config.TELEGRAM_API_TOKEN)
dp = Dispatcher()
router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    markup = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="🛍️ បើកហាងទំនិញ", web_app=WebAppInfo(url=config.MINI_APP_URL))]], 
        resize_keyboard=True
    )
    # Zero Omission: Kh/En Start text maintained
    await message.answer(f"🇰🇭 <b>Pizz King Streamer Engine V3.1</b>\nYour ID: <code>{message.from_user.id}</code>", reply_markup=markup, parse_mode="HTML")

# 2. SERVER ORCHESTRATION
async def main():
    dp.include_router(router)
    app = web.Application()

    # --- SECURE PRODUCT PROXY ROUTES ---
    app.router.add_get('/get-products', ai_handler.get_products_proxy)
    app.router.add_get('/get-categories', ai_handler.get_categories_proxy)
    
    # --- AI CHAT ENDPOINTS ---
    app.router.add_post('/ai-chat', ai_handler.process_chat_endpoint)
    app.router.add_options('/ai-chat', ai_handler.process_chat_endpoint) # Required for CORS
    
    # --- CORE STORE LOGIC (V1.0 Sync Kept) ---
    app.router.add_get("/", lambda r: web.Response(text="Pizz King Sovereign System V3.1 Online"))
    app.router.add_post("/create-order", woo_handler.create_order_endpoint)
    app.router.add_options("/create-order", woo_handler.create_order_endpoint)
    
    # --- VIDEO STREAMING (MTProto Bridge) ---
    app.router.add_get("/stream/{message_id}", video_streamer.stream_movie_endpoint)

    # 🚀 STARTUP SEQUENCE
    # Ignite MTProto Video Streamer
    await video_streamer.stream_client.start()

    # Ignite Web Server (Port managed by Render/VPS)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()
    
    logging.info("System V3.1 Dispatcher Online. Roster Synchronized.")
    
    # Start Polling and handle clean shutdown
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await video_streamer.stream_client.stop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
