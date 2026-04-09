// nav.js - MASTER BOTTOM NAVIGATION ENGINE V2.3
// Zero-Omission Protocol: Ultra-Slim & Panel-Aligned (480px)

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
        `background: ${activeBg}; border-radius: 8px; padding: 4px 6px; color: ${activeColor}; font-weight: 700;` : 
        `color: ${inactiveColor}; font-weight: 400;`;

    const navHTML = `
    <nav style="position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); width: 100%; max-width: 480px; height: 50px; background: #ffffff; border-top: 1px solid #f2f2f2; display: flex; justify-content: space-around; align-items: center; z-index: 2500; box-shadow: 0 -5px 20px rgba(0,0,0,0.05); padding-bottom: env(safe-area-inset-bottom); border-radius: 15px 15px 0 0;">
        
        <a href="index.html" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; font-size: 0.6rem; transition: 0.2s; width: 20%; ${getActiveBox('home')}">
            <svg viewBox="0 0 24 24" style="width: 20px; height: 20px; fill: currentColor;"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>
            <span>ទំព័រដើម</span>
        </a>

        <a href="sale.html" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; font-size: 0.6rem; transition: 0.2s; width: 20%; ${getActiveBox('sale')}">
            <svg viewBox="0 0 24 24" style="width: 20px; height: 20px; fill: currentColor;"><path d="M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z"/></svg>
            <span>បញ្ចុះតម្លៃ</span>
        </a>

        <div style="position: relative; top: -12px; text-align: center; width: 20%;">
            <a href="movie.html" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; transition: 0.2s;">
                <div style="width: 44px; height: 44px; background: #111111; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2); border: 2px solid #ffffff; margin-bottom: 2px;">
                    <svg viewBox="0 0 24 24" style="width: 22px; height: 22px; fill: #ffffff;"><path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-2z"/></svg>
                </div>
                <span style="font-size: 0.6rem; font-weight: 800; color: ${activePage === 'movies' ? activeColor : '#111111'};">មើលកុន</span>
            </a>
        </div>

        <a href="orders.html" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; font-size: 0.6rem; transition: 0.2s; width: 20%; ${getActiveBox('orders')}">
            <svg viewBox="0 0 24 24" style="width: 20px; height: 20px; fill: currentColor;"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
            <span>បញ្ជីទិញ</span>
        </a>

        <a href="javascript:void(0)" onclick="openTelegramContact(event)" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; font-size: 0.6rem; width: 20%; color: #0088cc;">
            <svg viewBox="0 0 24 24" style="width: 20px; height: 20px; fill: currentColor;"><path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894 8.221l-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.14.14-.24.24-.465.24l.215-3.048 5.548-5.013c.24-.213-.054-.334-.373-.121l-6.86 4.32-2.956-.924c-.642-.204-.658-.642.136-.95l11.55-4.45c.538-.196 1.006.128.832.934z"/></svg>
            <span>ជំនួយ</span>
        </a>
    </nav>
    `;
    const placeholder = document.getElementById('bottom-nav-placeholder');
    if (placeholder) { placeholder.innerHTML = navHTML; }
}
