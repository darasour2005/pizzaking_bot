// shopcart-payment.js - MASTER CART & PAYMENT LOGIC
// Zero-Omission Protocol: 100% Original Logic Preserved

function saveCartToStorage() { localStorage.setItem('pizz_king_cart_v36', JSON.stringify(cart)); }

function saveFormData() { 
    const nameInput = document.getElementById('user-name');
    const phoneInput = document.getElementById('user-phone');
    const locInput = document.getElementById('user-loc');
    
    if(nameInput) localStorage.setItem('pizz_king_name', nameInput.value); 
    if(phoneInput) localStorage.setItem('pizz_king_tel', phoneInput.value); 
    if(locInput) localStorage.setItem('pizz_king_loc', locInput.value); 
    
    // CRITICAL: Triggers instant recalculation when typing location
    updateCartBasedOnDelivery();
    checkForm(); 
}

function addToCart(pid) {
    const p = allProducts.find(x => x.id === pid); const q = cardQtys[pid] || 1;
    let name = p.name, price = parseFloat(p.price), cid = pid.toString();
    if (p.type === 'variable') {
        const vid = variationSelections[pid]; if (!vid) { tg.showAlert("សូមរើសប្រភេទ!"); return; }
        const vData = productVariations[pid].find(v => v.id == vid);
        name = `${p.name} (${vData.attributes[0].option})`; price = parseFloat(vData.price); cid = `${pid}-${vid}`;
    }
    const existing = cart.find(i => i.cartId.toString() === cid.toString());
    if(existing) existing.qty += q; else cart.push({ cartId: cid, id: pid, name, price, qty: q });
    saveCartToStorage(); updateCartBasedOnDelivery();
    const t = document.getElementById('toast'); t.style.display='flex'; setTimeout(() => t.style.display='none', 2000);
}

function updateCartBasedOnDelivery() {
    const realItems = cart.filter(i => !i.cartId.toString().startsWith('delivery')); if(realItems.length === 0) { cart = []; updateUI([]); return; }
    const subtotal = realItems.reduce((s, i) => s + (i.price * i.qty), 0);
    
    const locInput = document.getElementById('user-loc');
    const locRaw = locInput ? locInput.value.toLowerCase() : ""; 
    
    cart = realItems;
    if(locRaw.length > 3) {
        const isSR = APP_CONFIG.DELIVERY.siem_reap_keywords.some(k => locRaw.includes(k));
        let fee = isSR ? (subtotal < APP_CONFIG.DELIVERY.siem_reap_free_over_riel ? APP_CONFIG.DELIVERY.siem_reap_charge_riel : 0) : (subtotal < APP_CONFIG.DELIVERY.other_location_threshold_riel ? APP_CONFIG.DELIVERY.other_location_charge_below_riel : APP_CONFIG.DELIVERY.other_location_charge_over_or_equal_riel);
        if(fee > 0) cart.push({ cartId: "delivery", id: "delivery", name: "ថ្លៃដឹកជញ្ជូន", price: fee, qty: 1 });
    }
    updateUI(cart);
}

function updateUI(itemsList) {
    const show = itemsList.length > 0; document.getElementById('footer-ui').style.display = show ? 'block' : 'none';
    const total = itemsList.reduce((s, i) => s + (i.price * i.qty), 0);
    document.getElementById('cart-count').innerText = `🛒 កន្ត្រក: ${itemsList.filter(i => !i.cartId.toString().startsWith('delivery')).length} មុខ (មើលលម្អិត)`;
    document.getElementById('cart-total').innerText = `${total.toLocaleString()}៛`;
    document.getElementById('cart-list').innerHTML = itemsList.map(i => `<div class="cart-item-row"><div>${i.name}<br><small>${i.price.toLocaleString()}៛</small></div><div style="display:flex;align-items:center;justify-content:center;gap:10px;">${i.cartId.toString().startsWith('delivery') ? '' : `<button class="qty-btn" onclick="updateCartItemQty('${i.cartId}',-1)">−</button>`}<span>${i.qty}</span>${i.cartId.toString().startsWith('delivery') ? '' : `<button class="qty-btn" onclick="updateCartItemQty('${i.cartId}',1)">+</button>`}</div><button class="cart-del-btn" onclick="removeFromCart('${i.cartId}')"><svg viewBox="0 0 24 24" style="width:16px;height:16px;fill:red;"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg></button></div>`).join('');
    checkForm();
}

function checkForm() {
    const nameInput = document.getElementById('user-name');
    const phoneInput = document.getElementById('user-phone');
    const locInput = document.getElementById('user-loc');
    
    const n = nameInput ? nameInput.value : "";
    const p = phoneInput ? phoneInput.value : "";
    const l = locInput ? locInput.value : "";
    
    const hasItems = cart.filter(i => !i.cartId.toString().startsWith('delivery')).length > 0;
    const btn = document.getElementById('pre-pay-btn'); 
    const isValid = (n.length > 1 && p.length > 8 && l.length > 3 && hasItems);
    btn.disabled = !isValid; 
    
    if(isValid) {
        btn.style.background = "#2ecc71";
        btn.innerHTML = `<svg viewBox="0 0 24 24" style="width:20px;height:20px;fill:white;margin-right:8px;vertical-align:middle;"><path d="M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"/></svg><span style="vertical-align:middle;">ទូទាត់ប្រាក់ឥឡូវនេះ</span>`; 
    } else {
        btn.style.background = "#bdc3c7";
        btn.innerHTML = "ចាប់ផ្តើមបំពេញព័ត៌មានដឹកជញ្ជូន"; 
    }
}

function openPayment() {
    const total = cart.reduce((s, i) => s + (i.price * i.qty), 0);
    document.getElementById('pay-amt-label').innerText = total.toLocaleString();
    document.getElementById('recap-list').innerHTML = cart.map(i => `<div class="recap-row"><span>${i.name} x${i.qty}</span><span>${(i.price * i.qty).toLocaleString()}៛</span></div>`).join('') + `<div style="border-top:2px solid #eee; margin-top:10px; padding-top:10px; display:flex; justify-content:space-between; font-weight:800;"><span>សរុប៖</span><span>${total.toLocaleString()}៛</span></div>`;
    document.getElementById('payment-screen').style.display = 'flex';
    const dynamicQR = generateDynamicABAQR(total);
    document.getElementById('dynamic-khqr').src = `https://api.qrserver.com/v1/create-qr-code/?size=400x400&data=${encodeURIComponent(dynamicQR)}`;
    startTimer(900);
}

async function downloadQRImage() {
    const target = document.getElementById('invoice-card');
    const canvas = await html2canvas(target, { scale: 3, useCORS: true, logging: false });
    const link = document.createElement('a'); link.download = 'PizzKing_Receipt.png'; link.href = canvas.toDataURL("image/png"); link.click();
}

async function submitFinalOrder() {
    const btn = document.getElementById('confirm-btn'); btn.innerHTML = "⏳ កំពុងបញ្ជូន..."; btn.disabled = true;
    const total = cart.reduce((s, i) => s + (i.price * i.qty), 0);
    const userName = document.getElementById('user-name') ? document.getElementById('user-name').value : "";
    const userPhone = document.getElementById('user-phone') ? document.getElementById('user-phone').value : "";
    const userLoc = document.getElementById('user-loc') ? document.getElementById('user-loc').value : "";
    
    const orderData = { telegram_id: tg.initDataUnsafe.user?.id || 12345, name: userName, phone: userPhone, location: userLoc, items: cart, total, note: customerNote, auto_create_account: true, account_email: userPhone + "@phsar.me", account_pass: "Nprk@Angkor203" };
    
    try {
        await fetch(`${APP_CONFIG.RENDER_URL}/create-order`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(orderData) });
        localStorage.removeItem('pizz_king_cart_v36'); localStorage.setItem('pizz_user_phone', userPhone);
        document.getElementById('success-name-kh').innerText = userName; document.getElementById('success-name-en').innerText = userName;
        document.getElementById('payment-screen').style.display = 'none'; document.getElementById('success-modal').style.display = 'flex';
    } catch (e) { tg.showAlert("⚠️ Connection Error"); btn.innerHTML = `<svg viewBox="0 0 24 24" style="width:20px;height:20px;fill:white;"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg><span>ខ្ញុំបានបង់ប្រាក់រួចរាល់</span>`; btn.disabled = false; }
}

function toggleRecap() { const list = document.getElementById('recap-list'); const qrWrap = document.getElementById('qr-container'); const caret = document.getElementById('recap-caret'); if (list.style.display === 'block') { list.style.display = 'none'; qrWrap.style.display = 'block'; caret.innerText = '▼'; } else { list.style.display = 'block'; qrWrap.style.display = 'none'; caret.innerText = '▲'; } }
function openNote() { document.getElementById('note-input').value = customerNote; document.getElementById('note-modal').style.display = 'flex'; }
function closeNote() { document.getElementById('note-modal').style.display = 'none'; }
function saveNote() { customerNote = document.getElementById('note-input').value; document.getElementById('note-btn').innerText = "✅ ចំណាំ"; closeNote(); }
function toggleCart() { document.getElementById('cart-list').classList.toggle('open'); document.getElementById('cart-header').classList.toggle('open'); }
function closePay() { document.getElementById('payment-screen').style.display = 'none'; }
function updateCartItemQty(cid, d) { const i = cart.find(x => x.cartId.toString() === cid.toString()); if (i && !i.cartId.toString().startsWith('delivery')) { i.qty = Math.max(1, i.qty + d); updateCartBasedOnDelivery(); } }
function removeFromCart(cid) { cart = cart.filter(x => x.cartId.toString() !== cid.toString()); updateCartBasedOnDelivery(); }
function startTimer(d) { let t = d; setInterval(() => { let m = parseInt(t/60,10), s = parseInt(t%60,10); document.getElementById('pay-timer').textContent = (m<10?"0"+m:m)+":"+(s<10?"0"+s:s); if(--t < 0) t=0; }, 1000); }
