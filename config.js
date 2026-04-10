// config.js - MASTER FRONTEND CONFIGURATION

const APP_CONFIG = {
    // Render.com Python Backend URL (FIXED: Underscore instead of hyphen)
    RENDER_URL: "https://pizzaking-bot.onrender.com",
    
    // WordPress Database Endpoint
    WC_BASE: "https://1.phsar.me/wp-json/wc/v3",
    
    // WordPress API Keys (Read-Only/Customer Level)
    WC_AUTH: "?consumer_key=ck_",
    
    // Delivery Configuration
    DELIVERY: {
        siem_reap_keywords: ["siem reap", "សៀមរាប", "ខេត្តសៀមរាប"],
        siem_reap_free_over_riel: 40000, 
        siem_reap_charge_riel: 3000, 
        other_location_threshold_riel: 80000, 
        other_location_charge_below_riel: 8000, 
        other_location_charge_over_or_equal_riel: 11000
    }
};
