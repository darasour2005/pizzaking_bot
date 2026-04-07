import os
import json
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- ARCHITECT CONFIG ---
API_TOKEN = '8581539352:AAGByoBXhKj26xq2WPZkMdtsIUeYfpaDg6A'
# Replace with your actual ACLEDA/Bakong ID (e.g. alex@acleda)
MERCHANT_ID = "pizzking@acleda" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def load_products():
    with open('products.json', 'r', encoding='utf-8') as f:
        return json.load(f)

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    products = load_products()
    markup = InlineKeyboardMarkup(row_width=1)
    
    for p in products:
        # Khmer-Priority: បញ្ជាទិញ (Order)
        btn = InlineKeyboardButton(
            text=f"🛒 {p['name']} - ${p['price']}", 
            callback_data=f"buy_{p['id']}"
        )
        markup.add(btn)
        
    await message.answer("🍕 ស្វាគមន៍មកកាន់ Pizza King!\nសូមជ្រើសរើសមុខទំនិញខាងក្រោម៖", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data.startswith('buy_'))
async def process_buy(callback_query: types.CallbackQuery):
    product_id = int(callback_query.data.split('_')[1])
    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)
    
    if product:
        # Generate Simple KHQR Payment Link (Deep-Link for ACLEDA)
        # Standard: https://bakong.nbc.org.kh/download
        pay_text = (
            f"✅ អ្នកបានជ្រើសរើស: {product['name']}\n"
            f"💰 តម្លៃសរុប: ${product['price']}\n\n"
            f"សូមស្កេន QR ខាងក្រោម ឬចុចប៊ូតុងដើម្បីបង់ប្រាក់តាម ACLEDA"
        )
        
        # Pulse-Verify: This URL structure triggers the banking app directly
        acleda_deeplink = f"https://link.bakong.nbc.gov.kh/pay?id={MERCHANT_ID}&amount={product['price']}&currency=USD"
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💳 បង់ប្រាក់ឥឡូវនេះ (Pay Now)", url=acleda_deeplink))
        
        await bot.send_message(callback_query.from_user.id, pay_text, reply_markup=markup)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
