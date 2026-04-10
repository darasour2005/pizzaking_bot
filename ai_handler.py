# ai_handler.py - MASTER AI ORCHESTRATION ENGINE V3.6
# Zero-Omission Protocol: Secure Proxy + Async K2-5 + Reasoning Fix

import json
import logging
import asyncio
import os
import datetime
import pytz
import aiohttp
from aiohttp import web
from openai import AsyncOpenAI
import config
from woo_handler import wcapi

# 1. INITIALIZE KIMI (MOONSHOT) NEURAL NET
# Using the flagship model and the official CN endpoint
client = AsyncOpenAI(
    api_key=config.KIMI_API_KEY,
    base_url="https://api.moonshot.cn/v1"
)

# 2. SECURE PRODUCT PROXY (Protects your keys from index.html)
async def get_products_proxy(request):
    """Securely fetches products using backend keys to prevent frontend leaks."""
    headers = {"Access-Control-Allow-Origin": "*"}
    try:
        res = await asyncio.to_thread(wcapi.get, "products", params={"per_page": 100, "status": "publish"})
        return web.json_response(res.json(), headers=headers)
    except Exception as e:
        logging.error(f"Proxy Product Error: {e}")
        return web.json_response({"error": str(e)}, status=500, headers=headers)

async def get_categories_proxy(request):
    """Securely fetches categories using backend keys."""
    headers = {"Access-Control-Allow-Origin": "*"}
    try:
        res = await asyncio.to_thread(wcapi.get, "products/categories", params={"hide_empty": True, "parent": 0})
        return web.json_response(res.json(), headers=headers)
    except Exception as e:
        logging.error(f"Proxy Category Error: {e}")
        return web.json_response({"error": str(e)}, status=500, headers=headers)

# 3. DYNAMIC PROMPT INJECTION
def get_system_prompt():
    """Reads the AI rules and injects the live Cambodian clock."""
    fallback = "You are Dara's AI Sales Assistant for Pizza King. Use tools for inventory and orders."
    try:
        with open("system_prompt.txt", "r", encoding="utf-8") as f:
            base_prompt = f.read()
    except Exception:
        base_prompt = fallback
    current_time = datetime.datetime.now(pytz.timezone(config.TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
    return f"{base_prompt}\n\nCURRENT SYSTEM TIME: {current_time}"

# 4. TOOL DEFINITIONS (The AI's Hands)
KIMI_TOOLS = [
    {"type": "function", "function": {"name": "check_inventory", "description": "Fetch live products and prices.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "create_order", "description": "Create a real WooCommerce order.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "phone": {"type": "string"}, "product_ids": {"type": "array", "items": {"type": "integer"}}, "quantities": {"type": "array", "items": {"type": "integer"}}}, "required": ["name", "phone", "product_ids", "quantities"]}}},
    {"type": "function", "function": {"name": "get_order_details", "description": "Look up an order to check status and date.", "parameters": {"type": "object", "properties": {"order_id": {"type": "integer"}}, "required": ["order_id"]}}},
    {"type": "function", "function": {"name": "update_order_status", "description": "Update order to 'processing' or 'cancelled'.", "parameters": {"type": "object", "properties": {"order_id": {"type": "integer"}, "status": {"type": "string", "enum": ["processing", "cancelled"]}, "refund_needed": {"type": "boolean"}, "order_data": {"type": "string"}}, "required": ["order_id", "status"]}}},
    {"type": "function", "function": {"name": "add_order_note", "description": "Add a note to the WooCommerce order.", "parameters": {"type": "object", "properties": {"order_id": {"type": "integer"}, "note": {"type": "string"}}, "required": ["order_id", "note"]}}},
    {"type": "function", "function": {"name": "generate_invoice_link", "description": "Generate URL for PDF invoice.", "parameters": {"type": "object", "properties": {"order_id": {"type": "integer"}}, "required": ["order_id"]}}},
    {"type": "function", "function": {"name": "generate_checkout", "description": "Trigger ABA QR Code generation.", "parameters": {"type": "object", "properties": {"total_riel": {"type": "integer"}, "summary": {"type": "string"}}, "required": ["total_riel", "summary"]}}}
]

# 5. WORKERS
def woo_fetch_inventory():
    try:
        res = wcapi.get("products", params={"per_page": 20, "status": "publish"})
        return "\n".join([f"ID: {p['id']} | {p['name']}: {p['price']}៛" for p in res.json()]) if res.status_code == 200 else "Error."
    except Exception as e: return str(e)

def woo_get_order_details(order_id):
    try:
        res = wcapi.get(f"orders/{order_id}")
        if res.status_code == 200:
            order = res.json()
            return json.dumps({"id": order['id'], "status": order['status'], "total": order['total'], "customer_name": order.get('billing', {}).get('first_name'), "customer_phone": order.get('billing', {}).get('phone')})
        return "Not found."
    except Exception as e: return str(e)

def woo_create_order(name, phone, product_ids, quantities):
    try:
        data = {"billing": {"first_name": name, "phone": phone}, "line_items": [{"product_id": pid, "quantity": qty} for pid, qty in zip(product_ids, quantities)]}
        res = wcapi.post("orders", data)
        return f"SUCCESS. Order ID: {res.json()['id']}" if res.status_code == 201 else "Failed."
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

async def send_telegram_alert(order_id, refund_needed, order_data_str):
    try:
        d = json.loads(order_data_str)
        text = f"🚨 <b>AI CANCELLATION</b>\nID: #{order_id}\nName: {d.get('customer_name')}\nPhone: {d.get('customer_phone')}\nRefund: {'YES' if refund_needed else 'NO'}"
        async with aiohttp.ClientSession() as s:
            await s.post(f"https://api.telegram.org/bot{config.TELEGRAM_API_TOKEN}/sendMessage", json={"chat_id": config.GROUP_CHAT_ID, "text": text, "parse_mode": "HTML"})
    except Exception: pass

# 6. MAIN CHAT ENDPOINT
async def process_chat_endpoint(request):
    headers = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type"}
    if request.method == "OPTIONS": return web.Response(status=200, headers=headers)
    try:
        data = await request.json()
        conversation_history = data.get("history", [])
        messages = [{"role": "system", "content": get_system_prompt()}] + conversation_history

        # Use flagship model with the correct hyphen
        response = await client.chat.completions.create(
            model="kimi-k2-5", 
            messages=messages, 
            tools=KIMI_TOOLS,
            tool_choice="auto",
            temperature=0.2,
            max_tokens=4096
        )
        response_message = response.choices[0].message
        
        if response_message.tool_calls:
            # FIX: Serialization to preserve "reasoning_content" and stop 400 errors
            assistant_msg = response_message.model_dump(exclude_none=True)
            if hasattr(response_message, 'reasoning_content') and response_message.reasoning_content:
                assistant_msg['reasoning_content'] = response_message.reasoning_content
                
            messages.append(assistant_msg)
            qr_action = None
            
            for tool_call in response_message.tool_calls:
                func = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                res = "Executed."

                if func == "check_inventory": res = await asyncio.to_thread(woo_fetch_inventory)
                elif func == "get_order_details": res = await asyncio.to_thread(woo_get_order_details, args.get("order_id"))
                elif func == "create_order": res = await asyncio.to_thread(woo_create_order, args.get("name"), args.get("phone"), args.get("product_ids"), args.get("quantities"))
                elif func == "update_order_status":
                    res = await asyncio.to_thread(woo_update_status, args.get("order_id"), args.get("status"))
                    if args.get("status") == "cancelled" and res == "SUCCESS":
                        asyncio.create_task(send_telegram_alert(args.get("order_id"), args.get("refund_needed"), args.get("order_data")))
                elif func == "add_order_note": res = await asyncio.to_thread(woo_add_note, args.get("order_id"), args.get("note"))
                elif func == "generate_invoice_link": res = f"Link: https://1.phsar.me/my-account/view-order/{args.get('order_id')}/"
                elif func == "generate_checkout":
                    qr_action = {"action": "show_qr", "checkout_data": {"total": args.get("total_riel"), "summary": args.get("summary")}}
                    res = "QR code displayed."

                messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": func, "content": res})
            
            final = await client.chat.completions.create(model="kimi-k2-5", messages=messages)
            payload = {"reply": final.choices[0].message.content, "action": "none"}
            if qr_action: payload.update(qr_action)
            return web.json_response(payload, headers=headers)

        return web.json_response({"reply": response_message.content, "action": "none"}, headers=headers)

    except Exception as e:
        logging.error(f"AI Handler Error: {e}")
        return web.json_response({"reply": "⚠️ V3.5 សុំទោស ប្រព័ន្ធមានបញ្ហាបន្តិចបន្តួច។ (System error.)", "action": "error"}, headers=headers)
