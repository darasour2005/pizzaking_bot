// pdf-generator.js - BILINGUAL INVOICE ENGINE V1.4 (Anti-Blank Fix)

async function generateInvoicePDF(data) {
    const loader = document.getElementById('loader');
    if (loader) loader.style.display = 'flex';

    try {
        // 1. Generate QR Base64 (CORS Fix)
        const qrString = generateDynamicABAQR(data.grandTotal);
        const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${encodeURIComponent(qrString)}`;
        
        let base64Qr = "";
        try {
            const response = await fetch(qrUrl);
            const blob = await response.blob();
            base64Qr = await new Promise((resolve) => {
                const reader = new FileReader();
                reader.onloadend = () => resolve(reader.result);
                reader.readAsDataURL(blob);
            });
        } catch (e) {
            base64Qr = qrUrl; 
        }

        // 2. Build Bilingual Table Items
        let itemsHTML = data.items.map(item => `
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #ddd; font-weight:700;">${item.name}</td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align:center;">${item.quantity}</td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align:right;">${item.total.toLocaleString()}៛</td>
            </tr>
        `).join('');

        if (data.shippingTotal > 0) {
            itemsHTML += `
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #ddd; color:#555;">🚚 ថ្លៃដឹកជញ្ជូន (Shipping)</td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align:center;">1</td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align:right;">${data.shippingTotal.toLocaleString()}៛</td>
            </tr>`;
        }

        // 3. Build Bilingual HTML Structure
        const htmlContent = `
            <div style="background: #ffffff; padding: 40px; box-sizing: border-box; color: #000000; font-family: 'Kantumruy Pro', sans-serif;">
                <div style="display: flex; justify-content: space-between; border-bottom: 3px solid #e74c3c; padding-bottom: 15px; margin-bottom: 20px;">
                    <div>
                        <div style="font-size: 1.8rem; font-weight: 800; color: #e74c3c; line-height:1.2;">វិក្កយបត្រ</div>
                        <div style="font-size: 1.2rem; font-weight: 800; color: #7f8c8d; letter-spacing: 2px;">INVOICE</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-weight: 700; font-size: 1.4rem; color: #2c3e50;">#${data.id}</div>
                        <div style="color: #7f8c8d; font-size: 0.9rem;">${data.date}</div>
                    </div>
                </div>
                
                <div style="display: flex; justify-content: space-between; margin-bottom: 40px;">
                    <div>
                        <div style="font-weight: 800; margin-bottom: 5px; font-size: 1rem; color: #2c3e50;">អតិថិជន (Billed To):</div>
                        <div style="font-weight: 700; font-size: 1.2rem;">${data.customerName}</div>
                        <div style="color: #555; margin-top: 5px; max-width: 300px; line-height: 1.5;">${data.customerAddress} <br>(Tel: ${data.phone})</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-weight: 800; margin-bottom: 5px; font-size: 1rem; color: #2c3e50;">ស្ថានភាព (Order Status):</div>
                        <div style="font-weight: 800; font-size: 1.2rem; color: #e74c3c;">${data.status}</div>
                    </div>
                </div>

                <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;">
                    <thead>
                        <tr>
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #2c3e50; background: #f8f9fa; font-weight: 800; font-size:0.85rem;">បរិយាយ (Description)</th>
                            <th style="padding: 12px; text-align: center; border-bottom: 2px solid #2c3e50; background: #f8f9fa; font-weight: 800; font-size:0.85rem;">ចំនួន (Qty)</th>
                            <th style="padding: 12px; text-align: right; border-bottom: 2px solid #2c3e50; background: #f8f9fa; font-weight: 800; font-size:0.85rem;">សរុប (Amount)</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${itemsHTML}
                    </tbody>
                </table>

                <div style="display: flex; justify-content: flex-end; font-size: 1.8rem; font-weight: 800; color: #e74c3c; margin-bottom: 40px;">
                    <div style="margin-right: 40px; color: #2c3e50; font-size: 1.2rem;">សរុប (Total):</div>
                    <div>${data.grandTotal.toLocaleString()}៛</div>
                </div>

                <div style="border: 2px dashed #bdc3c7; border-radius: 15px; padding: 25px; display: flex; align-items: center; justify-content: space-between; background: #fafafa;">
                    <div>
                        <h3 style="color: #e74c3c; margin: 0 0 5px 0; font-size: 1.3rem;">ស្កេនដើម្បីបង់ប្រាក់</h3>
                        <div style="color: #7f8c8d; font-size: 0.85rem; margin-bottom: 12px; font-weight: 700;">SCAN TO PAY</div>
                        
                        <p style="margin: 0 0 5px 0; font-size: 1rem; color: #2c3e50;">ឈ្មោះគណនី (Account Name): <br><strong style="font-weight: 800;">${APP_CONFIG?.ABA_NAME || 'SOUR DARA'}</strong></p>
                        <p style="margin: 10px 0 10px 0; font-size: 1rem; color: #2c3e50;">ទឹកប្រាក់ (Amount): <br><strong style="color: #e74c3c; font-weight: 800; font-size: 1.2rem;">${data.grandTotal.toLocaleString()} KHR</strong></p>
                        
                        <p style="margin: 0; font-size: 0.75rem; color: #7f8c8d; line-height:1.4;">គាំទ្រគ្រប់កម្មវិធីធនាគារ KHQR (ABA, ACLEDA, etc.)<br>Supports all KHQR banking apps.</p>
                    </div>
                    <div style="text-align: center; background: #fff; padding: 10px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
                        <img src="${base64Qr}" style="width: 150px; height: 150px; display: block; margin: 0 auto;">
                        <div style="font-weight: 800; font-size: 1.1rem; color: #e74c3c; margin-top: 5px;">KHQR</div>
                    </div>
                </div>

                <div style="margin-top: 40px; text-align: center; color: #95a5a6; border-top: 1px solid #eee; padding-top: 20px;">
                    <div style="font-size: 1rem; font-weight: 700; color: #2c3e50; margin-bottom: 5px;">សូមអរគុណសម្រាប់ការគាំទ្រ!</div>
                    <div style="font-size: 0.85rem;">Thank you for your business.</div>
                </div>
            </div>
        `;

        const opt = {
            margin: [10, 10, 10, 10],
            filename: `Invoice_${data.id}.pdf`,
            image: { type: 'jpeg', quality: 1 },
            html2canvas: { scale: 2, useCORS: true, letterRendering: true },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
        };

        await html2pdf().set(opt).from(htmlContent).save();

    } catch (err) {
        console.error("PDF Error:", err);
        alert("⚠️ បរាជ័យក្នុងការទាញយក PDF");
    } finally {
        if (loader) loader.style.display = 'none'; 
    }
}
