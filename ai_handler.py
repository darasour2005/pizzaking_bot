# ai_handler.py - MASTER AI ORCHESTRATION ENGINE V2.7
# Zero-Omission Protocol: AsyncOpenAI Upgrade (Non-Blocking Architecture)

import json
import logging
import asyncio
import os
import datetime
import pytz
import aiohttp
from aiohttp import web
from openai import AsyncOpenAI  # <-- CRITICAL UPGRADE: Async Client
import config
from woo_handler import wcapi

# 1. INITIALIZE KIMI (MOONSHOT) NEURAL NET ASYNCHRONOUSLY
client = AsyncOpenAI(  # <-- CRITICAL UPGRADE
    api_key=config.KIMI_API_KEY,
    base_url="https://api.moonshot.ai/v1"
)

# 2. DYNAMIC PROMPT INJECTION
def get_system_prompt():
    """Reads the AI rules and injects the live Cambodian clock."""
    try:
        with open("system_prompt.txt", "r", encoding="utf-8") as f:
            base_prompt = f.read()
            
        current_time = datetime.datetime.now(pytz.timezone(config.TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
        return f"{base_prompt}\n\nCURRENT SYSTEM TIME: {current_time}"
    except Exception as e:
        logging.error(f"Failed to load system_prompt.txt: {e}")
        return "You are a helpful AI assistant for Pizza King in Cambodia. Please help the customer."

# 3. TOOL DEFINITIONS (The AI's Hands)
KIMI_TOOLS = [
    # ... [Keep all exactly the same as V2.6: check_inventory, create_order, get_order_details, update_order_status, add_order_note, generate_invoice_link, generate_checkout] ...
    {
        "type": "function",
        "function": {"name": "check_inventory", "description": "Fetch live products and prices.", "parameters": {"type": "object", "properties": {}}}
    },
    {
        "type": "function",
        "function": {
            "name": "create_order",
            "description": "Create a real WooCommerce order.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "phone": {"type": "string"},
                    "product_ids": {"type": "array", "items": {"type": "integer"}},
                    "quantities": {"type": "array", "items": {"type": "integer"}}
                },
                "required": ["name", "phone", "product_ids", "quantities"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_details",
            "description": "Look up an order to check its date, status, total, and customer info.",
            "parameters": {"type": "object", "properties": {"order_id": {"type": "integer"}}, "required": ["order_id"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_order_status",
            "description": "Update an order to 'processing' (paid) or 'cancelled'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "integer"},
                    "status": {"type": "string", "enum": ["processing", "cancelled"]},
                    "refund_needed": {"type": "boolean"},
                    "order_data": {"type": "string"}
                },
                "required": ["order_id", "status"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_order_note",
            "description": "Add a note to the WooCommerce order.",
            "parameters": {"type": "object", "properties": {"order_id": {"type": "integer"}, "note": {"type": "string"}}, "required": ["order_id", "note"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_invoice_link",
            "description": "Generate the URL for PDF invoice.",
            "parameters": {"type": "object", "properties": {"order_id": {"type": "integer"}}, "required": ["order_id"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_checkout",
            "description": "Trigger the ABA QR Code generation.",
            "parameters": {"type": "object", "properties": {"total_riel": {"type": "integer"}, "summary": {"type": "string"}}, "required": ["total_riel", "summary"]}
        }
    }
]

# 4. WOOCOMMERCE & TELEGRAM WORKERS
def woo_fetch_inventory():
    try:
        res = wcapi.get("products", params={"per_page": 20, "status": "publish"})
        return "\n".join([f"ID: {p['id']} | {p['name']}: {p['price']}៛" for p in res.json()]) if res.status_code == 200 else "Failed."
    except Exception as e: return str(e)

def woo_get_order_details(order_id):
    try:
        res = wcapi.get(f"orders/{order_id}")
        if res.status_code == 200:
            order = res.json()
            return json.dumps({
                "id": order['id'], "status": order['status'], "date_created": order['date_created'],
                "total": order['total'], "customer_name": order.get('billing', {}).get('first_name', 'Unknown'),
                "customer_phone": order.get('billing', {}).get('phone', 'Unknown')
            })
        return "FAILED: Order not found."
    except Exception as e: return str(e)

def woo_create_order(name, phone, product_ids, quantities):
    try:
        line_items = [{"product_id": pid, "quantity": qty} for pid, qty in zip(product_ids, quantities)]
        data = {"billing": {"first_name": name, "phone": phone}, "line_items": line_items}
        res = wcapi.post("orders", data)
        if res.status_code == 201:
            order = res.json()
            return f"SUCCESS. Order ID: {order['id']}, Total: {order['total']}៛"
        return f"FAILED: {res.text}"
    except Exception as e: return str(e)

def woo_update_status(order_id, status):
    try:
        res = wcapi.put(f"orders/{order_id}", {"status": status})
        return "SUCCESS" if res.status_code == 200 else "FAILED"
    except Exception as e: return str(e)

def woo_add_note(order_id, note):
    try:
        res = wcapi.post(f"orders/{order_id}/notes", {"note": note})
        return "SUCCESS" if res.status_code == 201 else "FAILED"
    except Exception as e: return str(e)

def woo_get_invoice(order_id):
    return f"https://1.phsar.me/my-account/view-order/{order_id}/"

async def send_telegram_alert(order_id, refund_needed, order_data_str):
    try:
        order_data = json.loads(order_data_str) if order_data_str else {}
        total = order_data.get('total', 'Unknown')
        name = order_data.get('customer_name', 'Unknown')
        phone = order_data.get('customer_phone', 'Unknown')
        
        text = f"🚨 <b>AI ORDER CANCELLATION</b>\n📦 <b>Order ID:</b> #{order_id}\n👤 <b>Customer:</b> {name}\n📞 <b>Phone:</b> <code>{phone}</code>\n💵 <b>Total Amount:</b> {total}៛\n\n"
        
        if refund_needed: text += "🔴 <b>STATUS: PAID - REFUND REQUIRED</b>\n⚠️ Please check bank slips and process refund."
        else: text += "⚪ <b>STATUS: UNPAID</b>\nNo refund needed."
            
        url = f"https://api.telegram.org/bot{config.TELEGRAM_API_TOKEN}/sendMessage"
        payload = {"chat_id": config.GROUP_CHAT_ID, "text": text, "parse_mode": "HTML"}
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=payload)
    except Exception as e: logging.error(f"Telegram Alert Failed: {e}")

# 5. MAIN CHAT ENDPOINT
async def process_chat_endpoint(request):
    headers = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type"}
    if request.method == "OPTIONS": return web.Response(status=200, headers=headers)
        
    try:
        data = await request.json()
        conversation_history = data.get("history", [])
        current_system_prompt = get_system_prompt()
        messages = [{"role": "system", "content": current_system_prompt}] + conversation_history

        # CRITICAL FIX: await the Async client to prevent server freezing
        response = await client.chat.completions.create(model="kimi-k2.5", messages=messages, tools=KIMI_TOOLS, temperature=0.2)
        response_message = response.choices[0].message
        
        if response_message.tool_calls:
            messages.append(response_message)
            qr_action = None
            
            for tool_call in response_message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                result = "Executed."

                if func_name == "check_inventory": result = await asyncio.to_thread(woo_fetch_inventory)
                elif func_name == "get_order_details": result = await asyncio.to_thread(woo_get_order_details, args.get("order_id"))
                elif func_name == "create_order": result = await asyncio.to_thread(woo_create_order, args.get("name"), args.get("phone"), args.get("product_ids"), args.get("quantities"))
                elif func_name == "update_order_status":
                    status, order_id, refund_needed, order_data = args.get("status"), args.get("order_id"), args.get("refund_needed", False), args.get("order_data", "")
                    result = await asyncio.to_thread(woo_update_status, order_id, status)
                    if status == "cancelled" and result == "SUCCESS": asyncio.create_task(send_telegram_alert(order_id, refund_needed, order_data))
                elif func_name == "add_order_note": result = await asyncio.to_thread(woo_add_note, args.get("order_id"), args.get("note"))
                elif func_name == "generate_invoice_link": result = f"Invoice Link: {woo_get_invoice(args.get('order_id'))}"
                elif func_name == "generate_checkout":
                    qr_action = {"action": "show_qr", "checkout_data": {"total": args.get("total_riel"), "summary": args.get("summary")}}
                    result = "QR generated on user screen."

                messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": func_name, "content": result})
            
            # CRITICAL FIX: await the Async client for the second pass
            final_response = await client.chat.completions.create(model="kimi-k2.5", messages=messages)
            
            payload = {"reply": final_response.choices[0].message.content, "action": "none"}
            if qr_action: payload.update(qr_action)
            return web.json_response(payload, headers=headers)

        return web.json_response({"reply": response_message.content, "action": "none"}, headers=headers)

    except Exception as e:
        logging.error(f"AI Handler Error: {e}")
        return web.json_response({"reply": "⚠️ សុំទោស ប្រព័ន្ធមានបញ្ហាបន្តិចបន្តួច។ (System error.)", "action": "error"}, headers=headers)
