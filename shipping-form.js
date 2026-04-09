// shipping-form.js - STANDALONE SHIPPING UI COMPONENT V1.0

function loadShippingForm() {
    const formHTML = `
        <div class="order-form" style="background: #fff; padding: 15px; border-radius: 12px; margin-top: 15px; border: 1px solid var(--pizz-border);">
            <h4 style="margin:0 0 12px 0;">📍 ព័ត៌មានដឹកជញ្ជូន</h4>
            <div class="input-group" style="margin-bottom: 12px;">
                <label style="display: block; font-size: 0.75rem; margin-bottom: 4px; font-weight: 700; color: #7f8c8d;">ឈ្មោះ</label>
                <input type="text" id="user-name" oninput="saveFormData()" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; font-size: 0.9rem; outline: none; font-family: inherit;">
            </div>
            <div class="input-group" style="margin-bottom: 12px;">
                <label style="display: block; font-size: 0.75rem; margin-bottom: 4px; font-weight: 700; color: #7f8c8d;">លេខទូរស័ព្ទ</label>
                <input type="tel" id="user-phone" oninput="saveFormData(); checkForm();" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; font-size: 0.9rem; outline: none; font-family: inherit;">
            </div>
            <div class="input-group" style="margin-bottom: 12px;">
                <label style="display: block; font-size: 0.75rem; margin-bottom: 4px; font-weight: 700; color: #7f8c8d;">ទីតាំង/ផ្ទះ</label>
                <input type="text" id="user-loc" oninput="saveFormData(); checkForm();" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; font-size: 0.9rem; outline: none; font-family: inherit;">
            </div>
        </div>
    `;

    const placeholder = document.getElementById('shipping-form-placeholder');
    if (placeholder) {
        placeholder.innerHTML = formHTML;
    }
}
