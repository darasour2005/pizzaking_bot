// product-slider.js - FEATURED SALE ENGINE V1.0

function renderProductSlider(categoryId = 0) {
    const container = document.getElementById('product-slider-container');
    if (!container) return;

    // 1. Filter Logic: Only show items ON SALE
    // If categoryId is not 0, also filter by Category
    let saleItems = allProducts.filter(p => p.on_sale === true);
    
    if (categoryId !== 0) {
        saleItems = saleItems.filter(p => p.categories.some(c => c.id === categoryId));
    }

    // If no items are on sale for this category, hide the block
    if (saleItems.length === 0) {
        container.style.display = 'none';
        return;
    }

    container.style.display = 'block';
    container.innerHTML = `
        <div class="sale-label">🔥 បញ្ចុះតម្លៃពិសេស (Flash Sale)</div>
        <div class="product-slider-wrapper">
            <div class="product-slider-track" id="product-sale-track">
                ${saleItems.map(p => `
                    <div class="sale-slide" onclick="openDetail(${p.id})">
                        <div class="sale-badge">SALE</div>
                        <img src="${p.images[0]?.src || ''}">
                        <div class="sale-info">
                            <div class="sale-name">${p.name}</div>
                            <div class="sale-price-row">
                                <span class="old-price">${parseInt(p.regular_price).toLocaleString()}៛</span>
                                <span class="new-price">${parseInt(p.price).toLocaleString()}៛</span>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}
