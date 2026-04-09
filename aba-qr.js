// aba-qr.js - STANDALONE ABA KHQR GENERATOR V1.0

// 1. CRC16 Checksum Calculator (Standard for EMVCo QR Codes)
function crc16(d) { 
    let c = 0xFFFF; 
    for (let i = 0; i < d.length; i++) { 
        let x = ((c >> 8) ^ d.charCodeAt(i)) & 0xFF; 
        x ^= x >> 4; 
        c = ((c << 8) ^ (x << 12) ^ (x << 5) ^ x) & 0xFFFF; 
    } 
    return (c & 0xFFFF).toString(16).toUpperCase().padStart(4, '0'); 
}

// 2. Dynamic ABA KHQR Payload Generator
function generateDynamicABAQR(amt) {
    const prefix = "00020101021229450016abaakhppxxx@abaa01090872828270208ABA Bank40390006abaP2P0112864C75E859140209087282827520400005303116";
    const amtVal = amt.toString() + ".0";
    
    // Core Payload
    const payload = prefix + `54${(amtVal.length).toString().padStart(2, '0')}${amtVal}` + "5802KH5909SOUR DARA6010Phnom Penh";
    
    // Tag 99 containing the expiration timestamps
    const tag99 = `99340013${Date.now()}0113${Date.now()+31536000000}`;
    const full = payload + tag99 + "6304";
    
    // Append the CRC16 checksum at the end to validate the string
    return full + crc16(full);
}
