# ai_handler.py - MASTER AI ORCHESTRATION ENGINE V1.0
# Zero-Omission Protocol: Secure Moonshot API + WooCommerce Tool Calling

import json
import logging
import asyncio
from aiohttp import web
from openai import OpenAI
import config
from woo_handler import wcapi

# 1. INITIALIZE KIMI (MOONSHOT) NEURAL NET
client = OpenAI(
    api_key=config.KIMI_API_KEY,
    base_url="https://api.moonshot.cn/v1"
)

# 2. SYSTEM PROMPT (The AI's Personality and Rules)
SYSTEM_PROMPT = """
You are Dara's elite AI Sales Assistant for the 'Pizza King Store' in Siem Reap, Cambodia. 
You are friendly, highly professional, and speak fluent Khmer and English.
Your goal is to answer questions, suggest products (especially Mulberry Wine and Pizzas), and close sales.

RULES:
1. Always quote prices in Khmer Riel (៛).
2. If a user asks what you have, use the 'check_inventory' tool.
3. If a user says they want to buy, confirm their phone number, location, and the total price.
4. Once they confirm, you MUST use the 'generate_checkout' tool to ask for payment. Do not pretend to take money yourself.
"""

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
            "name": "generate_checkout",
            "description": "Trigger the ABA QR Code generation for the customer to pay.",
            "parameters": {
                "type": "object",
                "properties": {
                    "total_riel": {"type": "integer", "description": "Total amount in Riel"},
                    "phone": {"type": "string", "description": "Customer phone number"},
                    "summary": {"type": "string", "description": "Short summary of items (e.g., '1x Pizza, 2x Wine')"}
                },
                "required": ["total_riel", "phone", "summary"]
            }
        }
    }
]

# 4. BACKGROUND WORKERS (Pulse-Verify-Confirm Architecture)
def fetch_live_inventory():
    """Synchronous WooCommerce call wrapped safely."""
    try:
        response = wcapi.get("products", params={"per_page": 20, "status": "publish"})
        if response.status_code == 200:
            products = response.json()
            inventory = [f"{p['name']}: {p['price']}៛" for p in products]
            return "\n".join(inventory)
        return "Error checking inventory."
    except Exception as e:
        logging.error(f"Inventory Fetch Error: {e}")
        return "Store system offline."

async def process_chat_endpoint(request):
    """
    The main API route that the frontend ai-chat.js talks to.
    """
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    
    if request.method == "OPTIONS":
        return web.Response(status=200, headers=headers)
        
    try:
        data = await request.json()
        user_message = data.get("message", "")
        conversation_history = data.get("history", []) # Array of previous messages
        
        # Build the exact message structure Kimi needs
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        # Step 1: Send to Kimi
        response = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=messages,
            tools=KIMI_TOOLS,
            temperature=0.3 # Keep the AI focused on sales, not hallucinating
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        action_payload = None # Used to tell the frontend to show a QR code

        # Step 2: Did Kimi decide to use a tool?
        if tool_calls:
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                if function_name == "check_inventory":
                    # Kimi wants to know what's in stock
                    inventory_data = await asyncio.to_thread(fetch_live_inventory)
                    messages.append(response_message)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": inventory_data
                    })
                    
                    # Pulse-Verify: Ask Kimi to reply again now that it has the inventory
                    second_response = client.chat.completions.create(
                        model="moonshot-v1-8k",
                        messages=messages
                    )
                    return web.json_response({
                        "reply": second_response.choices[0].message.content,
                        "action": "none"
                    }, headers=headers)

                elif function_name == "generate_checkout":
                    # Kimi is closing the sale!
                    total = arguments.get("total_riel", 0)
                    summary = arguments.get("summary", "")
                    
                    # Instead of creating the order instantly, we generate the checkout UI
                    # The frontend will render the QR code using JS based on this action
                    reply_text = f"អរគុណសម្រាប់ការកម្ម៉ង់! (Thank you for your order!)\n\nសរុប: {total}៛\n\nសូមធ្វើការស្កេន QR Code ខាងក្រោមដើម្បីទូទាត់ប្រាក់។ (Please scan the QR below to pay.)"
                    
                    return web.json_response({
                        "reply": reply_text,
                        "action": "show_qr",
                        "checkout_data": {
                            "total": total,
                            "summary": summary
                        }
                    }, headers=headers)

        # Step 3: Normal text response (No tools used)
        return web.json_response({
            "reply": response_message.content,
            "action": "none"
        }, headers=headers)

    except Exception as e:
        logging.error(f"AI Handler Error: {e}")
        return web.json_response({"reply": "⚠️ សុំទោស ប្រព័ន្ធមានបញ្ហាបន្តិចបន្តួច។ (System busy, please try again.)", "action": "error"}, headers=headers)
