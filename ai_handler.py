# ai_handler.py - MASTER AI ORCHESTRATION ENGINE V2.1
# Zero-Omission Protocol: Decoupled Prompt Architecture + Full WooCommerce Autonomy

import json
import logging
import asyncio
import os
from aiohttp import web
from openai import OpenAI
import config
from woo_handler import wcapi

# 1. INITIALIZE KIMI (MOONSHOT) NEURAL NET
client = OpenAI(
    api_key=config.KIMI_API_KEY,
    base_url="https://api.moonshot.cn/v1"
)

# 2. DYNAMIC PROMPT INJECTION
def get_system_prompt():
    """Reads the AI personality and rules from an external text file."""
    try:
        # Strict utf-8 encoding is required to safely read Khmer characters and the Riel (៛) symbol
        with open("system_prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logging.error(f"Failed to load system_prompt.txt: {e}")
        # Emergency fallback just in case the file is deleted
        return "You are a helpful AI assistant for Pizza King in Cambodia. Please help the customer."

# 3. TOOL DEFINITIONS (The AI's Hands)
KIMI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_inventory",
            "description": "Fetch live products and prices from the WooCommerce store.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_order",
            "description": "Create a real WooCommerce order.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Customer's first name"},
                    "phone": {"type": "string", "description": "Customer's phone number"},
                    "product_ids": {"type": "array", "items": {"type": "integer"}, "description": "List of Product IDs to buy"},
                    "quantities": {"type": "array", "items": {"type": "integer"}, "description": "List of quantities matching the product IDs"}
                },
                "required": ["name", "phone", "product_ids", "quantities"]
            }
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
                    "status": {"type": "string", "enum": ["processing", "cancelled"]}
                },
                "required": ["order_id", "status"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_order_note",
            "description": "Add a note to the WooCommerce order (e.g., saving that a slip was uploaded).",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "integer"},
                    "note": {"type": "string"}
                },
                "required": ["order_id", "note"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_invoice_link",
            "description": "Generate the URL for the customer to download their PDF invoice.",
            "parameters": {
                "type": "object",
                "properties": {"order_id": {"type": "integer"}},
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_checkout",
            "description": "Trigger the ABA QR Code generation for the customer to pay.",
            "parameters": {
                "type": "object",
                "properties": {
                    "total_riel": {"type": "integer"},
                    "summary": {"type": "string"}
                },
                "required": ["total_riel", "summary"]
            }
        }
    }
]

# 4. WOOCOMMERCE WORKERS (Pulse-Verify-Confirm Architecture)
def woo_fetch_inventory():
    try:
        res = wcapi.get("products", params={"per_page": 20, "status": "publish"})
        return "\n".join([f"ID: {p['id']} | {p['name']}: {p['price']}៛" for p in res.json()]) if res.status_code == 200 else "Failed."
    except Exception as e: return str(e)

def woo_create_order(name, phone, product_ids, quantities):
    try:
        line_items = [{"product_id": pid, "quantity": qty} for pid, qty in zip(product_ids, quantities)]
        data = {
            "billing": {"first_name": name, "phone": phone},
            "line_items": line_items
        }
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
    # Assuming standard WooCommerce Customer Invoice endpoint
    return f"https://1.phsar.me/my-account/view-order/{order_id}/"

# 5. MAIN CHAT ENDPOINT
async def process_chat_endpoint(request):
    headers = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type"}
    if request.method == "OPTIONS": return web.Response(status=200, headers=headers)
        
    try:
        data = await request.json()
        user_message, conversation_history = data.get("message", ""), data.get("history", [])
        
        # Inject the external text file into the brain instantly
        current_system_prompt = get_system_prompt()
        
        messages = [{"role": "system", "content": current_system_prompt}] + conversation_history + [{"role": "user", "content": user_message}]

        # Step 1: Kimi Processing
        response = client.chat.completions.create(model="moonshot-v1-8k", messages=messages, tools=KIMI_TOOLS, temperature=0.2)
        response_message = response.choices[0].message
        
        # Step 2: Intercept Tool Calls
        if response_message.tool_calls:
            messages.append(response_message)
            qr_action = None
            
            for tool_call in response_message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                result = "Executed."

                if func_name == "check_inventory":
                    result = await asyncio.to_thread(woo_fetch_inventory)
                elif func_name == "create_order":
                    result = await asyncio.to_thread(woo_create_order, args.get("name"), args.get("phone"), args.get("product_ids"), args.get("quantities"))
                elif func_name == "update_order_status":
                    result = await asyncio.to_thread(woo_update_status, args.get("order_id"), args.get("status"))
                elif func_name == "add_order_note":
                    result = await asyncio.to_thread(woo_add_note, args.get("order_id"), args.get("note"))
                elif func_name == "generate_invoice_link":
                    result = f"Invoice Link: {woo_get_invoice(args.get('order_id'))}"
                elif func_name == "generate_checkout":
                    qr_action = {"action": "show_qr", "checkout_data": {"total": args.get("total_riel"), "summary": args.get("summary")}}
                    result = "QR generated on user screen."

                messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": func_name, "content": result})
            
            # Step 3: Pulse-Verify (Let Kimi read the tool results and talk back to the user)
            final_response = client.chat.completions.create(model="moonshot-v1-8k", messages=messages)
            
            payload = {"reply": final_response.choices[0].message.content, "action": "none"}
            if qr_action: payload.update(qr_action)
            return web.json_response(payload, headers=headers)

        # Normal Response
        return web.json_response({"reply": response_message.content, "action": "none"}, headers=headers)

    except Exception as e:
        logging.error(f"AI Handler Error: {e}")
        return web.json_response({"reply": "⚠️ សុំទោស ប្រព័ន្ធមានបញ្ហាបន្តិចបន្តួច។ (System error.)", "action": "error"}, headers=headers)
