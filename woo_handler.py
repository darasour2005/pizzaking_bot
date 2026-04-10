# woo_handler.py - DEDICATED WOOCOMMERCE & ORDER ENGINE V1.2
# Zero-Omission Protocol: Background Failure Alerts + Variation Logic Preserved

import logging
import html
import asyncio
import json
from datetime import datetime
import pytz
from aiohttp import web
from woocommerce import API
import config

# 1. INITIALIZE WOOCOMMERCE ENGINE
wcapi = API(
    url=config.WC_URL, 
    consumer_key=config.WC_KEY, 
    consumer_secret=config.WC_SECRET, 
    version="wc/v3", 
    timeout=15
)

def background_wc_sync(order_payload, report_text):
    """
    Synchronous background worker. 
    Now includes a fail-safe Telegram alert if the sync crashes.
    """
    # Import bot here to avoid circular dependencies
    from main import bot
    
    try:
        res = wcapi.post("orders", order_payload)
        if res.status_code != 201:
            raise Exception(f"WooCommerce Error: {res.text}")
            
    except Exception as e:
        logging.error(f"Critical WC Sync Failure: {e}")
        
        # ERROR PROTOCOL: Alert Dara immediately via Telegram if sync fails
        error_msg = (
            f"⚠️ <b>CRITICAL: WOOCOMMERCE SYNC FAILED</b>\n"
            f"The following order was sent to Telegram but <b>NOT</b> saved to your website!\n\n"
            f"<b>Error:</b> {str(e)}\n\n"
            f"{report_text}"
        )
        
        # Create a temporary loop to send the emergency message
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot.send_message(config.GROUP_CHAT_ID, error_msg, parse_mode="HTML"))
        loop.close()

async def create_order_endpoint(request):
    """
    Handles the high-performance order injection from Mini App to WP.
    """
    from main import bot
    
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
        
        # SANITIZE INPUTS (Immutable Ledger V1 Logic)
        name = html.escape(str(data.get('name', 'N/A')))
        phone = html.escape(str(data.get('phone', 'N/A')))
        loc = html.escape(str(data.get('location', 'N/A')))
        note = html.escape(str(data.get('note', '')))
        items = data.get('items', [])
        total = data.get('total', 0)
        account_email = data.get('account_email', f"{phone}@phsar.me") 

        kh_tz = pytz.timezone('Asia/Phnom_Penh')
        now = datetime.now(kh_tz)
        order_date = now.strftime("%d-%m-%Y")
        order_time = now.strftime("%H:%M")

        # 1. FORMAT ITEM LISTS
        item_list_str = ""
        wp_line_items = []
        wp_shipping_lines = []

        for i in items:
            i_name = html.escape(str(i['name']))
            i_qty = int(i['qty'])
            i_price = float(i['price'])
            
            item_list_str += f"• {i_name} x{i_qty} — {int(i_price * i_qty):,}៛\n"
            
            # WP Logic: Separate delivery from real products
            if str(i.get('id')) == 'delivery':
                wp_shipping_lines.append({
                    "method_id": "flat_rate",
                    "method_title": "ថ្លៃដឹកជញ្ជូន (Delivery)",
                    "total": str(i_price * i_qty)
                })
            else:
                # Support for variations (ID format "123-456")
                clean_id = str(i['id']).split('-')[0]
                if clean_id.isdigit():
                    item_payload = {
                        "product_id": int(clean_id),
                        "quantity": i_qty
                    }
                    # Add variation ID if present
                    if '-' in str(i['id']):
                        item_payload["variation_id"] = int(str(i['id']).split('-')[1])
                    
                    wp_line_items.append(item_payload)
        
        note_display = f"\n📝 <b>ចំណាំ៖</b> {note}" if note.strip() else "\n📝 <b>ចំណាំ៖</b> គ្មាន"

        # 2. CONSTRUCT MASTER HTML REPORT
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

        # 3. SEND TELEGRAM MESSAGES
        await bot.send_message(config.GROUP_CHAT_ID, report_text, parse_mode="HTML")
        if tid and str(tid) != "12345":
            await bot.send_message(tid, f"✅ <b>ការកម្ម៉ង់បានជោគជ័យ!</b>\n\n{report_text}", parse_mode="HTML")

        # 4. WOOCOMMERCE SYNC (Non-Blocking Thread)
        wc_payload = {
            "status": "processing",
            "billing": {
                "first_name": name, 
                "address_1": loc, 
                "phone": phone,
                "email": account_email 
            },
            "line_items": wp_line_items,
            "shipping_lines": wp_shipping_lines,
            "customer_note": f"{note} (Time: {order_date} {order_time})",
        }
        
        # OFF-LOAD TO BACKGROUND
        asyncio.create_task(asyncio.to_thread(background_wc_sync, wc_payload, report_text))

        return web.json_response({"status": "success"}, headers=headers)
        
    except Exception as e:
        logging.error(f"API Endpoint Error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500, headers=headers)
