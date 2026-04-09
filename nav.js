// nav.js - MASTER BOTTOM NAVIGATION ENGINE V1.2
function loadBottomNav(activePage) {
    const navHTML = `
    <nav style="position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); width: 100%; max-width: 480px; height: 65px; background: #ffffff; border-top: 1px solid #eeeeee; display: flex; justify-content: space-around; align-items: center; z-index: 100; box-shadow: 0 -2px 10px rgba(0,0,0,0.03);">
        <a href="index.html" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; color: ${activePage === 'home' ? '#e74c3c' : '#95a5a6'}; font-size: 0.65rem; font-weight: 700; width: 60px;">
            <svg viewBox="0 0 24 24" style="width: 24px; height: 24px; fill: currentColor; margin-bottom: 3px;"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>
            ទំព័រដើម
        </a>
        <a href="sale.html" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; color: ${activePage === 'sale' ? '#e74c3c' : '#95a5a6'}; font-size: 0.65rem; font-weight: 700; width: 60px;">
            <svg viewBox="0 0 24 24" style="width: 24px; height: 24px; fill: currentColor; margin-bottom: 3px;"><path d="M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z"/></svg>
            បញ្ចុះតម្លៃ
        </a>
        <a href="orders.html" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; color: ${activePage === 'orders' ? '#e74c3c' : '#95a5a6'}; font-size: 0.65rem; font-weight: 700; width: 60px;">
            <svg viewBox="0 0 24 24" style="width: 24px; height: 24px; fill: currentColor; margin-bottom: 3px;"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
            បញ្ជីទិញ
        </a>
        <a href="movie.html" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; color: ${activePage === 'movies' ? '#e74c3c' : '#95a5a6'}; font-size: 0.65rem; font-weight: 700; width: 60px;">
            <svg viewBox="0 0 24 24" style="width: 24px; height: 24px; fill: currentColor; margin-bottom: 3px;"><path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-2z"/></svg>
            មើលកុន
        </a>
    </nav>
    `;
    const placeholder = document.getElementById('bottom-nav-placeholder');
    if (placeholder) { placeholder.innerHTML = navHTML; }
}
