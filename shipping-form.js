// shipping-form.js - 100% ORIGINAL LOGIC & LOOK
function loadShippingForm() {
    const placeholder = document.getElementById('shipping-form-placeholder');
    if (!placeholder) return;

    placeholder.innerHTML = `
        <div class="card" style="margin-top:20px; padding:20px; border:2px dashed #ddd;">
            <h3 style="margin:0 0 15px 0; color:var(--pizz-red); font-size:1.1rem;">📍 ព័ត៌មានដឹកជញ្ជូន (Shipping Info)</h3>
            <div style="margin-bottom:15px; text-align:left;">
                <label style="display:block; font-size:0.8rem; color:#7f8c8d; margin-bottom:5px; font-weight:700;">ឈ្មោះរបស់អ្នក / Name</label>
                <input type="text" id="user-name" oninput="saveFormData()" placeholder="ឈ្មោះ..." style="width:100%; padding:12px; border:1px solid #ddd; border-radius:8px; box-sizing:border-box;">
            </div>
            <div style="margin-bottom:15px; text-align:left;">
                <label style="display:block; font-size:0.8rem; color:#7f8c8d; margin-bottom:5px; font-weight:700;">លេខទូរស័ព្ទ / Phone</label>
                <input type="tel" id="user-phone" oninput="saveFormData()" placeholder="លេខទូរស័ព្ទ..." style="width:100%; padding:12px; border:1px solid #ddd; border-radius:8px; box-sizing:border-box;">
            </div>
            <div style="margin-bottom:5px; text-align:left;">
                <label style="display:block; font-size:0.8rem; color:#7f8c8d; margin-bottom:5px; font-weight:700;">ទីតាំងបច្ចុប្បន្ន / Location</label>
                <input type="text" id="user-loc" oninput="saveFormData()" placeholder="ឧទាហរណ៍៖ ភ្នំពេញ..." style="width:100%; padding:12px; border:1px solid #ddd; border-radius:8px; box-sizing:border-box;">
            </div>
        </div>
    `;
    // Restore saved state immediately
    const nameInput = document.getElementById('user-name');
    const phoneInput = document.getElementById('user-phone');
    const locInput = document.getElementById('user-loc');
    if(nameInput) nameInput.value = localStorage.getItem('pizz_king_name') || (window.Telegram.WebApp.initDataUnsafe.user ? window.Telegram.WebApp.initDataUnsafe.user.first_name : "");
    if(phoneInput) phoneInput.value = localStorage.getItem('pizz_king_tel') || "";
    if(locInput) locInput.value = localStorage.getItem('pizz_king_loc') || "";
}
