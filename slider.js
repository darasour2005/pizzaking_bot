// slider.js - MOVIE PROMO ENGINE V1.0
function initSlider() {
    const sliderData = [
        { img: "https://image.tmdb.org/t/p/w500/8Gxv8ZnlsuSqzZCUpa2sxb9O9Uz.jpg", link: "movie.html" },
        { img: "https://image.tmdb.org/t/p/w500/1E5baAaEse26fej7uHcjS3Ky0S2.jpg", link: "movie.html" },
        { img: "https://image.tmdb.org/t/p/w500/mD60Yp7IatSTun9Z9oXpSTGvSNo.jpg", link: "movie.html" },
        { img: "https://image.tmdb.org/t/p/w500/u3YvU2UNisOM0sWF2Zoufe9SxtM.jpg", link: "movie.html" },
        { img: "https://image.tmdb.org/t/p/w500/A76tUvNf99797mB0sES9ff7YpAc.jpg", link: "movie.html" }
    ];

    const container = document.getElementById('slider-container');
    if (!container) return;

    container.innerHTML = `
        <div class="main-slider">
            <div class="slider-track" id="slider-track">
                ${sliderData.map(s => `<div class="slide"><img src="${s.img}" onclick="location.href='${s.link}'"></div>`).join('')}
            </div>
            <div class="slider-dots" id="slider-dots"></div>
        </div>
    `;

    let current = 0;
    const track = document.getElementById('slider-track');
    const dots = document.getElementById('slider-dots');
    
    // Create dots
    sliderData.forEach((_, i) => {
        const dot = document.createElement('div');
        dot.className = `dot ${i === 0 ? 'active' : ''}`;
        dots.appendChild(dot);
    });

    setInterval(() => {
        current = (current + 1) % sliderData.length;
        track.style.transform = `translateX(-${current * 100}%)`;
        document.querySelectorAll('.dot').forEach((d, i) => d.classList.toggle('active', i === current));
    }, 4000);
}
