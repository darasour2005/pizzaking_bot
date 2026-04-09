// pwa.js - MASTER PWA & SMART GUARD ENGINE V1.4

let deferredPrompt;

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
        }
        deferredPrompt = null;
    } else {
        // Fallback for iOS/Safari where native prompt is blocked
        alert("សូមចុចលើប៊ូតុង Share ខាងក្រោម រួចរើសយក 'Add to Home Screen' (បន្ថែមទៅអេក្រង់ដើម)");
    }
}

// 3. Smart Guard Engine (Detects Telegram & PWA Status)
function initPWAGuard() {
    const isPWA = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone;
    const tg = window.Telegram ? window.Telegram.WebApp : null;
    const isTelegram = tg && tg.initData !== "";

    const guard = document.getElementById('install-guard');
    
    // If NOT a PWA and NOT inside Telegram, block the screen
    if (guard && !isPWA && !isTelegram) {
        guard.style.display = 'flex';
    }

    // 4. Register Service Worker quietly in the background
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('sw.js').catch(() => {
            console.log("Service Worker Registration bypassed.");
        });
    }
}

// Run the engine as soon as the DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPWAGuard);
} else {
    initPWAGuard();
}
