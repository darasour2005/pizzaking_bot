# woo_handler.py - DEDICATED WOOCOMMERCE & ORDER ENGINE
import logging
import html
from datetime import datetime
import pytz
from aiohttp import web
from woocommerce import API
import config

# Initialize WooCommerce Engine exactly as previously defined
wcapi = API(
    url=config.WC_URL, 
    consumer_key=config.WC_KEY, 
    consumer_secret=config.WC_SECRET, 
    version="wc/v3", 
    timeout=15
)

async def create_order_endpoint(request):
    """
    Handles the high-performance order injection from Mini App to WP.
    Logic carried forward: Zero Omission Protocol.
    """
    # Import bot here to avoid circular imports if needed
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
        
        # SANITIZE ALL INPUTS (Immutable Ledger V1 Logic)
        name = html.escape(str(data.get('name', 'N/A')))
        phone = html.escape(str(data.get('phone', 'N/A')))
        loc = html.escape(str(data.get('location', 'N/A')))
        note = html.escape(str(data.get('note', '')))
        items = data.get('items', [])
        total = data.get('total', 0)
        account_email = data.get('account_email', '') 
        
        kh_tz = pytz.timezone('Asia/Phnom_Penh')
        now = datetime.now(kh_tz)
        order_date = now.strftime("%d-%m-%Y")
        order_time = now.strftime("%H:%M")

        # 1. Format Item List & Separate Shipping for WP
        item_list_str = ""
        wp_line_items = []
        wp_shipping_lines = []

        for i in items:
            i_name = html.escape(str(i['name']))
            i_qty = int(i['qty'])
            i_price = float(i['price'])
            
            item_list_str += f"• {i_name} x{i_qty} — {int(i_price * i_qty):,}៛\n"
            
            # WP Logic: Separate delivery from real products (Historical Sync V1)
            if str(i.get('id')) == 'delivery':
                wp_shipping_lines.append({
                    "method_id": "flat_rate",
                    "method_title": "ថ្លៃដឹកជញ្ជូន (Delivery)",
                    "total": str(i_price * i_qty)
                })
            elif str(i.get('id')).split('-')[0].isdigit(): # Handle variation IDs (e.g., "123-456")
                wp_line_items.append({
                    "product_id": int(str(i['id']).split('-')[0]),
                    "quantity": i_qty
                })
        
        note_display = f"\n📝 <b>ចំណាំ៖</b> {note}" if note.strip() else "\n📝 <b>ចំណាំ៖</b> គ្មាន"

        # 2. Construct Master HTML Report for Telegram
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
        try:
            await bot.send_message(config.GROUP_CHAT_ID, report_text, parse_mode="HTML")
        except Exception as e:
            logging.error(f"Group Send Error: {e}")

        if tid:
            try:
                await bot.send_message(tid, f"✅ <b>ការកម្ម៉ង់បានជោគជ័យ!</b>\n\n{report_text}", parse_mode="HTML")
            except Exception as e:
                logging.error(f"Buyer Send Error: {e}")

        # 4. WOOCOMMERCE SYNC
        try:
            wcapi.post("orders", {
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
            })
        except Exception as e:
            logging.error(f"WC Sync Error: {e}")

        return web.json_response({"status": "success"}, headers=headers)
        
    except Exception as e:
        logging.error(f"API Endpoint Error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500, headers=headers)
