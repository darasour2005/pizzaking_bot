// nav.js - The Master Navigation Engine

function loadBottomNav(activePage) {
    const navHTML = `
    <nav class="bottom-nav-bar">
        <a href="index.html" class="nav-item ${activePage === 'home' ? 'active' : ''}">
            <svg viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>
            ទំព័រដើម
        </a>
        <a href="#" class="nav-item ${activePage === 'sale' ? 'active' : ''}">
            <svg viewBox="0 0 24 24"><path d="M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z"/></svg>
            បញ្ចុះតម្លៃ
        </a>
        <a href="orders.html" class="nav-item ${activePage === 'orders' ? 'active' : ''}">
            <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
            បញ្ជីទិញ
        </a>
        <a href="movie.html" class="nav-item ${activePage === 'movies' ? 'active' : ''}">
            <svg viewBox="0 0 24 24"><path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-2z"/></svg>
            មើលកុន
        </a>
    </nav>
    `;

    // Inject the menu into the placeholder on the page
    const placeholder = document.getElementById('bottom-nav-placeholder');
    if (placeholder) {
        placeholder.innerHTML = navHTML;
    }
}
