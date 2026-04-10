// nav.js - MASTER BOTTOM NAVIGATION ENGINE V2.7
// Zero-Omission Protocol: 6-Slot Architecture + Pizza King Red AI Button

function openTelegramContact(e) {
    e.preventDefault();
    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initData !== "") { 
        window.Telegram.WebApp.openTelegramLink('https://t.me/+85587282827'); 
    } else { 
        window.open('https://t.me/+85587282827', '_blank'); 
    }
}

function loadBottomNav(activePage) {
    const activeColor = '#e74c3c'; 
    const activeBg = 'rgba(231, 76, 60, 0.08)'; 
    const inactiveColor = '#7f8c8d'; 

    const getActiveBox = (page) => activePage === page ? 
        `background: ${activeBg}; border-radius: 8px; padding: 6px 4px; color: ${activeColor}; font-weight: 700;` : 
        `color: ${inactiveColor}; font-weight: 400; padding: 6px 4px;`;

    const navHTML = `
    <nav style="position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); width: 100%; max-width: 480px; height: 65px; background: #ffffff; border-top: 1px solid #f2f2f2; display: flex; justify-content: space-between; align-items: center; z-index: 2500; box-shadow: 0 -5px 20px rgba(0,0,0,0.05); padding-bottom: env(safe-area-inset-bottom); border-radius: 15px 15px 0 0; padding-left: 5px; padding-right: 5px;">
        
        <a href="index.html" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; font-size: 0.7rem; transition: 0.2s; flex: 1; ${getActiveBox('home')}">
            <svg viewBox="0 0 24 24" style="width: 24px; height: 24px; fill: currentColor; margin-bottom: 3px;"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>
            <span style="white-space: nowrap;">ទំព័រដើម</span>
        </a>

        <a href="sale.html" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; font-size: 0.7rem; transition: 0.2s; flex: 1; ${getActiveBox('sale')}">
            <svg viewBox="0 0 24 24" style="width: 24px; height: 24px; fill: currentColor; margin-bottom: 3px;"><path d="M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z"/></svg>
            <span style="white-space: nowrap;">បញ្ចុះតម្លៃ</span>
        </a>

        <div style="position: relative; top: -16px; text-align: center; flex: 1.2;">
            <a href="javascript:void(0)" onclick="if(window.AIChatEngine) { AIChatEngine.toggleChat(); } else { alert('AI is loading...'); }" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; transition: 0.2s;">
                <div style="width: 52px; height: 52px; background: #e74c3c; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(231, 76, 60, 0.4); border: 3px solid #ffffff; margin-bottom: 4px; margin-left: auto; margin-right: auto;">
                    <svg viewBox="0 0 24 24" style="width: 26px; height: 26px; fill: #ffffff;"><path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.38-1 1.73V7h5a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-1v2a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1v-2H6a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h5V5.73c-.6-.35-1-.99-1-1.73a2 2 0 0 1 2-2M7.5 13A1.5 1.5 0 0 0 6 14.5A1.5 1.5 0 0 0 7.5 16A1.5 1.5 0 0 0 9 14.5A1.5 1.5 0 0 0 7.5 13m9 0a1.5 1.5 0 0 0-1.5 1.5 1.5 1.5 0 0 0 1.5 1.5 1.5 1.5 0 0 0 1.5-1.5 1.5 1.5 0 0 0-1.5-1.5M12 9c-2.21 0-4 1.79-4 4h8c0-2.21-1.79-4-4-4z"/></svg>
                </div>
                <span style="font-size: 0.75rem; font-weight: 800; color: #e74c3c; white-space: nowrap;">ប្រើខ្ញុំ</span>
            </a>
        </div>

        <a href="orders.html" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; font-size: 0.7rem; transition: 0.2s; flex: 1; ${getActiveBox('orders')}">
            <svg viewBox="0 0 24 24" style="width: 24px; height: 24px; fill: currentColor; margin-bottom: 3px;"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
            <span style="white-space: nowrap;">បញ្ជីទិញ</span>
        </a>

        <a href="movie.html" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; font-size: 0.7rem; transition: 0.2s; flex: 1; ${getActiveBox('movies')}">
            <svg viewBox="0 0 24 24" style="width: 24px; height: 24px; fill: currentColor; margin-bottom: 3px;"><path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-2z"/></svg>
            <span style="white-space: nowrap;">មើលកុន</span>
        </a>

        <a href="javascript:void(0)" onclick="openTelegramContact(event)" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; font-size: 0.7rem; flex: 1; color: #0088cc; padding: 6px 4px;">
            <svg viewBox="0 0 24 24" style="width: 24px; height: 24px; fill: currentColor; margin-bottom: 3px;"><path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894 8.221l-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.14.14-.24.24-.465.24l.215-3.048 5.548-5.013c.24-.213-.054-.334-.373-.121l-6.86 4.32-2.956-.924c-.642-.204-.658-.642.136-.95l11.55-4.45c.538-.196 1.006.128.832.934z"/></svg>
            <span style="white-space: nowrap;">ជំនួយ</span>
        </a>
    </nav>
    `;
    const placeholder = document.getElementById('bottom-nav-placeholder');
    if (placeholder) { placeholder.innerHTML = navHTML; }
}
