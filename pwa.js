// pwa.js - MASTER PWA & SMART GUARD ENGINE V1.5
// Handles: 2-Week Snooze, Telegram Non-Blocking Banner, and Aggressive Cache Updates

let deferredPrompt;
const TWO_WEEKS_MS = 14 * 24 * 60 * 60 * 1000; // 14 days in milliseconds
const SNOOZE_KEY = 'pizz_pwa_snooze';

// 1. Capture the native install prompt
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
});

// 2. Handle the Install Button Click
async function installPWA() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        if (outcome === 'accepted') {
            const guard = document.getElementById('install-guard');
            if (guard) guard.style.display = 'none';
            const tgBanner = document.getElementById('tg-pwa-banner');
            if (tgBanner) tgBanner.style.display = 'none';
        }
        deferredPrompt = null;
    } else {
        // Fallback for iOS/Safari or Telegram Webview where native prompt is blocked
        alert("សូមចុចលើប៊ូតុង Share/Menu រួចរើសយក 'Add to Home Screen' (បន្ថែមទៅអេក្រង់ដើម)");
    }
}

// 3. Install Later (Snooze Function)
function installLater() {
    localStorage.setItem(SNOOZE_KEY, Date.now().toString());
    const guard = document.getElementById('install-guard');
    if (guard) guard.style.display = 'none';
}

// 4. Show Non-Blocking Telegram Banner
function showTelegramBanner() {
    if (sessionStorage.getItem('tg_banner_closed')) return; // Hide for this session if closed
    
    const banner = document.createElement('div');
    banner.id = 'tg-pwa-banner';
    banner.style.cssText = "position: fixed; top: 0; left: 50%; transform: translateX(-50%); width: 100%; max-width: 480px; background: #e74c3c; color: white; padding: 10px 15px; display: flex; align-items: center; justify-content: space-between; z-index: 9999; box-sizing: border-box; box-shadow: 0 4px 15px rgba(0,0,0,0.2); font-family: 'Kantumruy Pro', sans-serif;";
    
    banner.innerHTML = `
        <div style="flex-grow: 1; font-size: 0.75rem; font-weight: 700; line-height: 1.3;">
            បទពិសោធន៍ល្អជាងមុនជាមួយ App ផ្ទាល់!
        </div>
        <button onclick="installPWA()" style="background: white; color: #e74c3c; border: none; padding: 6px 12px; border-radius: 20px; font-weight: 700; font-size: 0.7rem; cursor: pointer; margin-right: 10px;">ដំឡើង</button>
        <button onclick="this.parentElement.style.display='none'; sessionStorage.setItem('tg_banner_closed', 'true');" style="background: none; border: none; color: white; font-size: 1.2rem; cursor: pointer; padding: 0;">×</button>
    `;
    document.body.appendChild(banner);
}

// 5. Master Guard Engine
function initPWAGuard() {
    const isPWA = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone;
    const tg = window.Telegram ? window.Telegram.WebApp : null;
    const isTelegram = tg && tg.initData !== "";

    // Rule A: If already installed, do absolutely nothing.
    if (isPWA) return; 

    // Rule B: Handle Telegram vs Standard Browser
    if (isTelegram) {
        showTelegramBanner(); // Show non-blocking banner
    } else {
        const guard = document.getElementById('install-guard');
        const lastSnooze = parseInt(localStorage.getItem(SNOOZE_KEY) || '0', 10);
        
        // Check if 2 weeks have passed since they clicked "Install Later"
        if (guard && (Date.now() - lastSnooze > TWO_WEEKS_MS)) {
            guard.style.display = 'flex';
            
            // Dynamically inject the "Install Later" button if it's not there
            if (!document.getElementById('btn-install-later')) {
                const laterBtn = document.createElement('button');
                laterBtn.id = 'btn-install-later';
                laterBtn.innerText = "ខ្ញុំនឹងដំឡើងពេលក្រោយ (Install Later)";
                laterBtn.style.cssText = "background: none; border: none; color: #95a5a6; font-weight: 700; margin-top: 20px; cursor: pointer; font-size: 0.85rem; text-decoration: underline;";
                laterBtn.onclick = installLater;
                guard.appendChild(laterBtn);
            }
        }
    }

    // 6. Aggressive Cache Busting (Force Update Engine)
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('sw.js').then(reg => {
            reg.onupdatefound = () => {
                const installingWorker = reg.installing;
                installingWorker.onstatechange = () => {
                    if (installingWorker.state === 'installed' && navigator.serviceWorker.controller) {
                        // A new version is found and installed. Force reload to clear old cache.
                        console.log("Pizza King App Updated. Reloading...");
                        window.location.reload(true);
                    }
                };
            };
        }).catch(err => console.log("SW Registration Failed:", err));
    }
}

// Fire the engine safely
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPWAGuard);
} else {
    initPWAGuard();
}
