// nav.js - MASTER BOTTOM NAVIGATION ENGINE V1.3
// Handles global Telegram linking safely
function openTelegramContact(e) {
    e.preventDefault();
    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initData !== "") { 
        window.Telegram.WebApp.openTelegramLink('https://t.me/+85587282827'); 
    } else { 
        window.open('https://t.me/+85587282827', '_blank'); 
    }
}

function loadBottomNav(activePage) {
    const activeColor = '#e74c3c'; // Pizza Red for active
    const inactiveColor = '#95a5a6'; // Elegant Gray for inactive

    const navHTML = `
    <nav style="position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); width: 100%; max-width: 480px; height: 65px; background: #ffffff; border-top: 1px solid #f0f0f0; display: flex; justify-content: space-around; align-items: center; z-index: 100; box-shadow: 0 -4px 20px rgba(0,0,0,0.05); padding-bottom: env(safe-area-inset-bottom);">
        <a href="index.html" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; color: ${activePage === 'home' ? activeColor : inactiveColor}; font-size: 0.65rem; font-weight: ${activePage === 'home' ? '700' : 'normal'}; width: 20%; transition: 0.2s;">
            <svg viewBox="0 0 24 24" style="width: 24px; height: 24px; fill: currentColor; margin-bottom: 4px; transition: transform 0.2s; ${activePage === 'home' ? 'transform: translateY(-2px);' : ''}"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>
            ទំព័រដើម
        </a>
        <a href="sale.html" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; color: ${activePage === 'sale' ? activeColor : inactiveColor}; font-size: 0.65rem; font-weight: ${activePage === 'sale' ? '700' : 'normal'}; width: 20%; transition: 0.2s;">
            <svg viewBox="0 0 24 24" style="width: 24px; height: 24px; fill: currentColor; margin-bottom: 4px; transition: transform 0.2s; ${activePage === 'sale' ? 'transform: translateY(-2px);' : ''}"><path d="M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z"/></svg>
            បញ្ចុះតម្លៃ
        </a>
        <a href="orders.html" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; color: ${activePage === 'orders' ? activeColor : inactiveColor}; font-size: 0.65rem; font-weight: ${activePage === 'orders' ? '700' : 'normal'}; width: 20%; transition: 0.2s;">
            <svg viewBox="0 0 24 24" style="width: 24px; height: 24px; fill: currentColor; margin-bottom: 4px; transition: transform 0.2s; ${activePage === 'orders' ? 'transform: translateY(-2px);' : ''}"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
            បញ្ជីទិញ
        </a>
        <a href="movie.html" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; color: ${activePage === 'movies' ? activeColor : inactiveColor}; font-size: 0.65rem; font-weight: ${activePage === 'movies' ? '700' : 'normal'}; width: 20%; transition: 0.2s;">
            <svg viewBox="0 0 24 24" style="width: 24px; height: 24px; fill: currentColor; margin-bottom: 4px; transition: transform 0.2s; ${activePage === 'movies' ? 'transform: translateY(-2px);' : ''}"><path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-2z"/></svg>
            មើលកុន
        </a>
        <a href="javascript:void(0)" onclick="openTelegramContact(event)" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; color: ${inactiveColor}; font-size: 0.65rem; font-weight: normal; width: 20%; transition: 0.2s;">
            <svg viewBox="0 0 24 24" style="width: 24px; height: 24px; fill: currentColor; margin-bottom: 4px;"><path d="M11.944 0C5.346 0 0 5.346 0 11.944c0 6.598 5.346 11.944 11.944 11.944 6.598 0 11.944-5.346 11.944-11.944C23.888 5.346 18.542 0 11.944 0zm5.642 8.358c-.161 1.696-.86 5.818-1.215 7.717-.15.805-.45 1.074-.728 1.101-.62.054-1.09-.413-1.689-.806-.94-.616-1.472-1-2.387-1.604-1.057-.698-.372-1.082.23-1.706.158-.163 2.905-2.664 2.958-2.887.007-.028.013-.131-.047-.184s-.149-.035-.213-.021c-.092.019-1.55 1.144-4.37 3.047-.413.284-.787.424-1.12.417-.367-.008-1.071-.208-1.595-.378-.642-.209-1.15-.319-1.106-.673.023-.185.276-.375.76-.569 2.967-1.293 4.945-2.146 5.934-2.558 2.825-1.177 3.412-1.381 3.795-1.387.084-.001.271.02.393.118.102.083.13.195.138.274.008.079.018.256.007.391z"/></svg>
            ជំនួយ
        </a>
    </nav>
    `;
    const placeholder = document.getElementById('bottom-nav-placeholder');
    if (placeholder) { placeholder.innerHTML = navHTML; }
}
