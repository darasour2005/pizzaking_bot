// mini-cart.js - 100% ORIGINAL LOGIC & LOOK
function renderMiniCart() {
    const container = document.getElementById('mini-cart-placeholder');
    if (!container) return;

    container.innerHTML = `
        <div class="footer-cart" id="footer-ui" style="display:none;">
            <div class="cart-header" id="cart-header">
                <span style="font-weight:700;display:flex;align-items:center;gap:10px;font-size:1.1rem;">🛒 ទំនិញដែលបានរើស</span>
                <button onclick="openNote()" style="background:#f0f2f5; border:1px dashed #ccc; border-radius:8px; padding:6px 12px; font-weight:700; cursor:pointer;" id="note-btn">➕ ចំណាំ</button>
                <button onclick="toggleCart()" style="background:none; border:none; font-size:32px; color:#ccc; cursor:pointer;">×</button>
            </div>
            <div id="cart-list" class="cart-details"></div>
            <div style="display:flex; justify-content:space-between; margin-bottom:15px; font-weight:700; cursor:pointer;" onclick="toggleCart()">
                <span id="cart-count">🛒 កន្ត្រក: ០ មុខ (មើលលម្អិត)</span><span id="cart-total">០៛</span>
            </div>
            <button class="checkout-btn" id="pre-pay-btn" onclick="openPayment()" disabled>ចាប់ផ្តើមបំពេញព័ត៌មានដឹកជញ្ជូន</button>
        </div>
    `;
}
