# woo_handler.py - DEDICATED WOOCOMMERCE & ORDER ENGINE V1.3
# Zero-Omission Protocol: Variation ID Parsing + Background Sync Alerts

import logging
import html
import asyncio
import json
from datetime import datetime
import pytz
from aiohttp import web
from woocommerce import API
import config

wcapi = API(
    url=config.WC_URL, 
    consumer_key=config.WC_KEY, 
    consumer_secret=config.WC_SECRET, 
    version="wc/v3", 
    timeout=15
)

def background_wc_sync(order_payload, report_text):
    from main import bot
    try:
        res = wcapi.post("orders", order_payload)
        if res.status_code != 201: raise Exception(f"WooCommerce Error: {res.text}")
    except Exception as e:
        logging.error(f"Critical WC Sync Failure: {e}")
        error_msg = f"⚠️ <b>CRITICAL: WOOCOMMERCE SYNC FAILED</b>\nError: {str(e)}\n\n{report_text}"
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot.send_message(config.GROUP_CHAT_ID, error_msg, parse_mode="HTML"))
        loop.close()

async def create_order_endpoint(request):
    from main import bot
    headers = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type"}
    if request.method == "OPTIONS": return web.Response(status=200, headers=headers)
        
    try:
        data = await request.json()
        tid = data.get('telegram_id')
        name = html.escape(str(data.get('name', 'N/A')))
        phone = html.escape(str(data.get('phone', 'N/A')))
        loc = html.escape(str(data.get('location', 'N/A')))
        note = html.escape(str(data.get('note', '')))
        items, total = data.get('items', []), data.get('total', 0)
        account_email = data.get('account_email', f"{phone}@phsar.me") 

        kh_tz = pytz.timezone('Asia/Phnom_Penh')
        now = datetime.now(kh_tz)
        order_date, order_time = now.strftime("%d-%m-%Y"), now.strftime("%H:%M")

        item_list_str, wp_line_items, wp_shipping_lines = "", [], []

        for i in items:
            i_name, i_qty, i_price = html.escape(str(i['name'])), int(i['qty']), float(i['price'])
            item_list_str += f"• {i_name} x{i_qty} — {int(i_price * i_qty):,}៛\n"
            
            if str(i.get('id')) == 'delivery':
                wp_shipping_lines.append({"method_id": "flat_rate", "method_title": "ថ្លៃដឹកជញ្ជូន (Delivery)", "total": str(i_price * i_qty)})
            else:
                # OMISSION CHECK: Preserved V1 Logic for Variation IDs ("123-456")
                clean_id = str(i['id']).split('-')[0]
                if clean_id.isdigit():
                    item_payload = {"product_id": int(clean_id), "quantity": i_qty}
                    if '-' in str(i['id']): item_payload["variation_id"] = int(str(i['id']).split('-')[1])
                    wp_line_items.append(item_payload)
        
        note_display = f"\n📝 <b>ចំណាំ៖</b> {note}" if note.strip() else "\n📝 <b>ចំណាំ៖</b> គ្មាន"
        report_text = f"🚀 <b>ការកម្ម៉ង់ថ្មី (Mini App)</b>\n📅 ថ្ងៃទី: <code>{order_date}</code> | ម៉ោង: <code>{order_time}</code>\n👤 ឈ្មោះ: <b>{name}</b>\n📞 លេខទូរស័ព្ទ: <code>{phone}</code>\n📍 ទីតាំង: <code>{loc}</code>{note_display}\n\n📦 <b>ទំនិញ៖</b>\n{item_list_str}\n💰 <b>សរុប៖ {int(total):,} ៛</b>"

        await bot.send_message(config.GROUP_CHAT_ID, report_text, parse_mode="HTML")
        if tid and str(tid) != "12345": await bot.send_message(tid, f"✅ <b>ការកម្ម៉ង់បានជោគជ័យ!</b>\n\n{report_text}", parse_mode="HTML")

        wc_payload = {"status": "processing", "billing": {"first_name": name, "address_1": loc, "phone": phone, "email": account_email}, "line_items": wp_line_items, "shipping_lines": wp_shipping_lines, "customer_note": f"{note} (Time: {order_date} {order_time})"}
        asyncio.create_task(asyncio.to_thread(background_wc_sync, wc_payload, report_text))

        return web.json_response({"status": "success"}, headers=headers)
    except Exception as e:
        logging.error(f"API Endpoint Error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500, headers=headers)
