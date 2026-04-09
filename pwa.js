// pwa.js - MASTER PWA & SMART GUARD ENGINE V1.8
// Highlights: Free Movies & Khmer Shopping + 3-Day Snooze Logic

let deferredPrompt;
const TWO_WEEKS_MS = 14 * 24 * 60 * 60 * 1000; 
const THREE_DAYS_MS = 3 * 24 * 60 * 60 * 1000; 
const SNOOZE_KEY = 'pizz_pwa_snooze';
const TG_SNOOZE_KEY = 'pizz_tg_pwa_snooze';

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
});

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
        alert("សូមចុចលើប៊ូតុង Share/Menu រួចរើសយក 'Add to Home Screen'");
    }
}

function installLater() {
    localStorage.setItem(SNOOZE_KEY, Date.now().toString());
    const guard = document.getElementById('install-guard');
    if (guard) guard.style.display = 'none';
}

function showTelegramBanner() {
    const lastTgSnooze = parseInt(localStorage.getItem(TG_SNOOZE_KEY) || '0', 10);
    if (Date.now() - lastTgSnooze < THREE_DAYS_MS) return;
    
    const banner = document.createElement('div');
    banner.id = 'tg-pwa-banner';
    // Attractive Red Gradient for Telegram Banner
    banner.style.cssText = "position: fixed; top: 0; left: 50%; transform: translateX(-50%); width: 100%; max-width: 480px; background: linear-gradient(90deg, #e74c3c, #c0392b); color: white; padding: 12px 15px; display: flex; align-items: center; justify-content: space-between; z-index: 9999; box-sizing: border-box; box-shadow: 0 4px 15px rgba(0,0,0,0.3); font-family: 'Kantumruy Pro', sans-serif; border-radius: 0 0 15px 15px;";
    
    banner.innerHTML = `
        <div style="flex-grow: 1; font-size: 0.8rem; font-weight: 700; line-height: 1.4;">
            🎬 មើលកុនហ្វ្រី និងទិញទំនិញងាយស្រួលក្នុង App!
        </div>
        <button onclick="installPWA()" style="background: white; color: #e74c3c; border: none; padding: 6px 14px; border-radius: 20px; font-weight: 800; font-size: 0.75rem; cursor: pointer; margin-right: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">ដំឡើង</button>
        <button onclick="this.parentElement.style.display='none'; localStorage.setItem('${TG_SNOOZE_KEY}', Date.now().toString());" style="background: none; border: none; color: white; font-size: 1.4rem; cursor: pointer; padding: 0;">×</button>
    `;
    document.body.appendChild(banner);
}

function initPWAGuard() {
    const isPWA = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone;
    const tg = window.Telegram ? window.Telegram.WebApp : null;
    const isTelegram = tg && tg.initData !== "";

    if (isPWA) {
        const guard = document.getElementById('install-guard');
        if (guard) guard.style.display = 'none';
    } 
    else if (isTelegram) {
        const guard = document.getElementById('install-guard');
        if (guard) guard.style.display = 'none';
        showTelegramBanner(); 
    } 
    else {
        const guard = document.getElementById('install-guard');
        const lastSnooze = parseInt(localStorage.getItem(SNOOZE_KEY) || '0', 10);
        if (guard && (Date.now() - lastSnooze > TWO_WEEKS_MS)) {
            guard.style.display = 'flex';
        }
    }

    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('sw.js').then(reg => {
            document.addEventListener('visibilitychange', () => {
                if (document.visibilityState === 'visible') reg.update();
            });
            reg.onupdatefound = () => {
                const installingWorker = reg.installing;
                installingWorker.onstatechange = () => {
                    if (installingWorker.state === 'installed' && navigator.serviceWorker.controller) {
                        window.location.reload(true);
                    }
                };
            };
        }).catch(err => console.log("SW Registration Failed:", err));
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPWAGuard);
} else {
    initPWAGuard();
}
