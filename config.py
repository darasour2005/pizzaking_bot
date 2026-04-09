# config.py - MASTER BACKEND CONFIGURATION V3.0
# Zero-Omission Protocol: All system-wide keys synchronized.

# --- TELEGRAM MTPROTO KEYS (From my.telegram.org) ---
# Used by video_streamer.py to bypass 20MB bot limits for movies.
API_ID = 20268624
API_HASH = '64ec010a2ebf0a756774876243018df1'

# --- TELEGRAM BOT ENGINE ---
# Used for order notifications and /start commands.
TELEGRAM_API_TOKEN = '8503376154:AAGsDQEaLHCq3E_ttoCAT46SygrD2VubP-E'
GROUP_CHAT_ID = '-1003499575831' 

# --- VIDEO STORAGE PROTOCOL ---
# The Private Channel ID where your movies are uploaded.
# Note: Private channel IDs must start with -100 for the MTProto client.
MOVIE_CHANNEL_ID = -1003914893548 

# --- WOOCOMMERCE ENGINE (WordPress) ---
# Used by woo_handler.py to sync orders with 1.phsar.me
WC_URL = "https://1.phsar.me"
WC_KEY = "ck_6a9c8caa18a2b0ab114ef90bb9e982d69521ec03"
WC_SECRET = "cs_63c256e1b4eba0a65723f054159e55d2148c3c57"

# --- FRONTEND ROUTING ---
# The base URL of your PWA for Telegram buttons.
MINI_APP_URL = "https://darasour2005.github.io/pizzaking_bot/"

# --- SYSTEM SETTINGS ---
# Timezone for Khmer report generation.
TIMEZONE = 'Asia/Phnom_Penh'
