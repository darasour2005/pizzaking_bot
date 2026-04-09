// nav.js - MASTER BOTTOM NAVIGATION ENGINE V2.0
// Zero-Omission Protocol: High-Class Bilingual UI

function openTelegramContact(e) {
    e.preventDefault();
    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initData !== "") { 
        window.Telegram.WebApp.openTelegramLink('https://t.me/+85587282827'); 
    } else { 
        window.open('https://t.me/+85587282827', '_blank'); 
    }
}

function loadBottomNav(activePage) {
    const activeColor = '#e74c3c'; // Pizza Red
    const activeBg = 'rgba(231, 76, 60, 0.08)'; // Fancy soft-red box
    const inactiveColor = '#95a5a6'; // Elegant Gray

    // Helper to generate the "Fancy Box" style if active
    const getActiveBox = (page) => activePage === page ? 
        `background: ${activeBg}; border-radius: 12px; padding: 6px 10px; color: ${activeColor}; font-weight: 700;` : 
        `color: ${inactiveColor}; font-weight: 400;`;

    const navHTML = `
    <nav style="position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); width: 100%; max-width: 500px; height: 75px; background: #ffffff; border-top: 1px solid #f0f0f0; display: flex; justify-content: space-around; align-items: center; z-index: 2500; box-shadow: 0 -10px 30px rgba(0,0,0,0.08); padding: 0 10px 15px 10px; border-radius: 25px 25px 0 0;">
        
        <a href="index.html" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; font-size: 0.65rem; transition: 0.3s; ${getActiveBox('home')}">
            <svg viewBox="0 0 24 24" style="width: 22px; height: 22px; fill: currentColor; margin-bottom: 2px;"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>
            ទំព័រដើម
        </a>

        <a href="sale.html" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; font-size: 0.65rem; transition: 0.3s; ${getActiveBox('sale')}">
            <svg viewBox="0 0 24 24" style="width: 22px; height: 22px; fill: currentColor; margin-bottom: 2px;"><path d="M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z"/></svg>
            បញ្ចុះតម្លៃ
        </a>

        <div style="position: relative; top: -15px; text-align: center;">
            <a href="movie.html" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; transition: 0.3s;">
                <div style="width: 58px; height: 58px; background: #1a1a1a; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 20px rgba(0,0,0,0.3); border: 3px solid #ffffff; margin-bottom: 4px;">
                    <svg viewBox="0 0 24 24" style="width: 28px; height: 28px; fill: #ffffff;"><path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-2z"/></svg>
                </div>
                <span style="font-size: 0.7rem; font-weight: 800; color: ${activePage === 'movies' ? activeColor : '#1a1a1a'};">មើលកុន</span>
            </a>
        </div>

        <a href="orders.html" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; font-size: 0.65rem; transition: 0.3s; ${getActiveBox('orders')}">
            <svg viewBox="0 0 24 24" style="width: 22px; height: 22px; fill: currentColor; margin-bottom: 2px;"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
            បញ្ជីទិញ
        </a>

        <a href="javascript:void(0)" onclick="openTelegramContact(event)" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; color: ${inactiveColor}; font-size: 0.65rem; transition: 0.3s;">
            <svg viewBox="0 0 24 24" style="width: 24px; height: 24px; fill: #0088cc; margin-bottom: 2px;">
                <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894 8.221l-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.14.14-.24.24-.465.24l.215-3.048 5.548-5.013c.24-.213-.054-.334-.373-.121l-6.86 4.32-2.956-.924c-.642-.204-.658-.642.136-.95l11.55-4.45c.538-.196 1.006.128.832.934z"/>
            </svg>
            ជំនួយ
        </a>
    </nav>
    `;
    const placeholder = document.getElementById('bottom-nav-placeholder');
    if (placeholder) { placeholder.innerHTML = navHTML; }
}
