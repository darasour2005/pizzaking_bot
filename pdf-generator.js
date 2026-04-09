// pdf-generator.js - STANDALONE INVOICE GENERATOR V1.0

function generateInvoicePDF(data) {
    // 1. Activate the global loader
    const loader = document.getElementById('loader');
    if (loader) loader.style.display = 'flex';

    // 2. Create the hidden container & CSS dynamically if it doesn't exist
    let container = document.getElementById('dynamic-invoice-container');
    if (!container) {
        const style = document.createElement('style');
        style.innerHTML = `
            #dynamic-invoice-container { position: absolute; left: -9999px; top: 0; width: 800px; background: #fff; padding: 40px; box-sizing: border-box; color: #000; font-family: 'Kantumruy Pro', sans-serif; }
            .inv-header { display: flex; justify-content: space-between; border-bottom: 2px solid #000; padding-bottom: 20px; margin-bottom: 20px; }
            .inv-title { font-size: 2.5rem; font-weight: 800; letter-spacing: 2px; }
            .inv-info-box { display: flex; justify-content: space-between; margin-bottom: 30px; }
            .inv-table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
            .inv-table th, .inv-table td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            .inv-table th { background: #f8f9fa; font-weight: 700; }
            .inv-total-row { display: flex; justify-content: flex-end; font-size: 1.5rem; font-weight: 800; }
        `;
        document.head.appendChild(style);

        container = document.createElement('div');
        container.id = 'dynamic-invoice-container';
        document.body.appendChild(container);
    }

    // 3. Build the Item Rows
    let itemsHTML = data.items.map(item => `
        <tr>
            <td style="font-weight:700;">${item.name}</td>
            <td style="text-align:center;">${item.quantity}</td>
            <td style="text-align:right;">${item.total.toLocaleString()}៛</td>
        </tr>
    `).join('');

    // Inject Shipping if exists
    if (data.shippingTotal > 0) {
        itemsHTML += `
        <tr>
            <td style="color:#555;">Delivery Fee</td>
            <td style="text-align:center;">1</td>
            <td style="text-align:right;">${data.shippingTotal.toLocaleString()}៛</td>
        </tr>`;
    }

    // 4. Inject the final HTML payload
    container.innerHTML = `
        <div class="inv-header">
            <div class="inv-title">INVOICE</div>
            <div style="text-align: right;">
                <div style="font-weight: 700; font-size: 1.2rem;">#${data.id}</div>
                <div style="color: #555;">${data.date}</div>
            </div>
        </div>
        <div class="inv-info-box">
            <div>
                <div style="font-weight: 800; margin-bottom: 5px; font-size: 1.1rem;">Billed To:</div>
                <div style="font-weight: 700;">${data.customerName}</div>
                <div style="color: #555; margin-top: 5px; max-width: 300px;">${data.customerAddress} <br>(Tel: ${data.phone})</div>
            </div>
            <div style="text-align: right;">
                <div style="font-weight: 800; margin-bottom: 5px; font-size: 1.1rem;">Status:</div>
                <div style="font-weight: 700; color: #2ecc71;">${data.status}</div>
            </div>
        </div>
        <table class="inv-table">
            <thead>
                <tr>
                    <th>បរិយាយ (Description)</th>
                    <th style="text-align: center;">ចំនួន (Qty)</th>
                    <th style="text-align: right;">សរុប (Amount)</th>
                </tr>
            </thead>
            <tbody>
                ${itemsHTML}
            </tbody>
        </table>
        <div class="inv-total-row">
            <div style="margin-right: 40px;">សរុប (Total):</div>
            <div>${data.grandTotal.toLocaleString()}៛</div>
        </div>
        <div style="margin-top: 50px; text-align: center; color: #7f8c8d; font-size: 0.9rem; border-top: 1px solid #eee; padding-top: 20px;">
            Thank you for your business.
        </div>
    `;

    // 5. Fire the PDF Library
    const opt = {
        margin:       10,
        filename:     `Invoice_${data.id}.pdf`,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, useCORS: true },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    html2pdf().set(opt).from(container).save().then(() => {
        if (loader) loader.style.display = 'none'; // Kill loader
    });
}
