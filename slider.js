// slider.js - SLIM MOVIE PROMO ENGINE V1.1
function initSlider() {
    // 5 High-Quality, Fast-Loading Movie Banners
    const movies = [
        { img: "https://images.alphacoders.com/134/1341054.jpeg", link: "movie.html" },
        { img: "https://wallpapercave.com/wp/wp12061005.jpg", link: "movie.html" },
        { img: "https://images7.alphacoders.com/131/1315518.jpg", link: "movie.html" },
        { img: "https://wallpaperaccess.com/full/1089154.jpg", link: "movie.html" },
        { img: "https://wallpapercave.com/wp/wp12140401.jpg", link: "movie.html" }
    ];

    const container = document.getElementById('slider-container');
    if (!container) return;

    container.innerHTML = `
        <div class="main-slider">
            <div class="slider-track" id="slider-track">
                ${movies.map(m => `
                    <div class="slide">
                        <img src="${m.img}" onclick="location.href='${m.link}'" onerror="this.src='https://via.placeholder.com/500x120?text=Pizza+King+Movies'">
                    </div>
                `).join('')}
            </div>
            <div class="slider-dots" id="slider-dots"></div>
        </div>
    `;

    let cur = 0;
    const track = document.getElementById('slider-track');
    const dotsContainer = document.getElementById('slider-dots');

    // Create Navigation Dots
    movies.forEach((_, i) => {
        const d = document.createElement('div');
        d.className = `dot ${i === 0 ? 'active' : ''}`;
        dotsContainer.appendChild(d);
    });

    // Auto-Run Logic
    setInterval(() => {
        cur = (cur + 1) % movies.length;
        if (track) {
            track.style.transform = `translateX(-${cur * 100}%)`;
            document.querySelectorAll('.dot').forEach((d, i) => d.classList.toggle('active', i === cur));
        }
    }, 4500);
}
