// mini-cart.js - UNIFIED SUMMARY & SHIPPING V1.0

function renderMiniCart() {
    const footer = document.getElementById('footer-ui-container');
    if (!footer) return;

    footer.innerHTML = `
        <div class="footer-cart" id="footer-ui" style="display:none;">
            <div class="cart-header" id="cart-header">
                <span style="font-weight:700; font-size:1.1rem;">🛒 ទំនិញដែលបានរើស</span>
                <div style="display:flex; gap:10px;">
                    <button onclick="openNote()" class="mini-btn">➕ ចំណាំ</button>
                    <button onclick="toggleCart()" class="mini-btn">×</button>
                </div>
            </div>

            <div id="cart-list" class="cart-details"></div>

            <div class="summary-bloc">
                <div class="summary-top" onclick="toggleCart()">
                    <span id="cart-count">🛒 កន្ត្រក: ០ មុខ</span>
                    <span id="cart-total" style="color:var(--pizz-red); font-weight:800;">០៛</span>
                </div>
                
                <div class="summary-actions">
                    <button class="shipping-trigger-btn" onclick="openShippingModal()">
                        📍 ព័ត៌មានដឹកជញ្ជូន <span id="shipping-status-icon">❌</span>
                    </button>
                    <button class="checkout-btn" id="pre-pay-btn" onclick="openPayment()" disabled>
                        ទូទាត់ប្រាក់
                    </button>
                </div>
            </div>
        </div>

        <div id="shipping-modal" class="modal-overlay">
            <div class="isolated-note-card">
                <button class="close-x" onclick="closeShippingModal()">×</button>
                <h3 style="margin:0 0 15px 0; color:var(--pizz-red);">📍 ព័ត៌មានដឹកជញ្ជូន</h3>
                <div class="input-group">
                    <label>ឈ្មោះរបស់អ្នក / Name</label>
                    <input type="text" id="user-name" oninput="saveFormData()" placeholder="ឈ្មោះ...">
                </div>
                <div class="input-group">
                    <label>លេខទូរស័ព្ទ / Phone</label>
                    <input type="tel" id="user-phone" oninput="saveFormData()" placeholder="លេខទូរស័ព្ទ...">
                </div>
                <div class="input-group">
                    <label>ទីតាំងបច្ចុប្បន្ន / Location</label>
                    <input type="text" id="user-loc" oninput="saveFormData()" placeholder="ឧទាហរណ៍៖ ភ្នំពេញ...">
                </div>
                <button class="btn-paid-final" onclick="closeShippingModal()" style="margin-top:15px;">យល់ព្រម (OK)</button>
            </div>
        </div>
    `;
}

function openShippingModal() { document.getElementById('shipping-modal').style.display = 'flex'; }
function closeShippingModal() { document.getElementById('shipping-modal').style.display = 'none'; }
