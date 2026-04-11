# ai_connector.py - AI NEURAL BRIDGE V1.2
# Zero-Omission: Variation Sight + Fractional Weights + Loyalty Tools

import logging
import json
import vertexai
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration
from openai import AsyncOpenAI
import config

vertexai.init(project="gen-lang-client-0110298481", location="asia-southeast1")
kimi_client = AsyncOpenAI(api_key=config.KIMI_API_KEY, base_url="https://api.moonshot.ai/v1")

# 1. TOOL DEFINITIONS (Empowered for Human-Flex Selling)
tools_list = [
    FunctionDeclaration(name="check_inventory", description="Fetch live products and variations (Box vs Kilo).", parameters={"type": "object", "properties": {}}),
    FunctionDeclaration(name="classify_customer", description="Identify if customer is LOYAL or FIRST_TIME.", parameters={"type": "object", "properties": {"phone": {"type": "string"}}, "required": ["phone"]}),
    FunctionDeclaration(name="create_order", description="Create order. Authorize discounts or 500g price_override here.", parameters={
        "type": "object",
        "properties": {
            "name": {"type": "string"}, "phone": {"type": "string"}, "telegram_id": {"type": "integer"},
            "items": {"type": "array", "items": {"type": "object", "properties": {"id": {"type": "string"}, "qty": {"type": "number"}, "price_override": {"type": "number"}}}},
            "discount": {"type": "number"}, "shipping_promo": {"type": "string"}
        }, "required": ["name", "phone", "items"]
    }),
    FunctionDeclaration(name="generate_invoice", description="Get A4/A5 image and fixed PDF link.", parameters={"type": "object", "properties": {"order_id": {"type": "integer"}, "size": {"type": "string"}}, "required": ["order_id"]})
]
GEMINI_TOOLS = Tool(function_declarations=tools_list)

async def get_ai_response(messages, user_input):
    try:
        # Default: Gemini 2.5 Flash-Lite (Cheapest)
        lite = GenerativeModel("gemini-2.5-flash-lite")
        intent = await lite.generate_content_async(f"Analyze: '{user_input}'. Reply 'TOOL' if ordering/stock/info, else 'CHAT'.")
        
        if "TOOL" in intent.text.upper():
            # Specialist: Gemini 3.1 Flash
            model = GenerativeModel("gemini-3.1-flash")
            response = await model.generate_content_async(messages, tools=[GEMINI_TOOLS])
            return response, "gemini-3.1-flash"
        return intent, "gemini-2.5-flash-lite"
    except Exception as e:
        # Emergency Backup: Kimi k2.5
        backup = await kimi_client.chat.completions.create(model="kimi-k2.5", messages=messages, temperature=1)
        return backup, "kimi-k2.5"
