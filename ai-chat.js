// ai-chat.js - MASTER AI INTERFACE V1.2
// Zero-Omission Protocol: Bottom-Nav Integrated & Properly Docked

const AIChatEngine = {
    chatHistory: [], // Memory buffer so Kimi remembers the conversation

    init: function() {
        this.injectCSS();
        this.injectHTML();
        this.attachListeners();
    },

    injectCSS: function() {
        const style = document.createElement('style');
        style.innerHTML = `
            /* Floating Widget Removed. Chat window now docks securely above 65px Bottom Nav */
            #ai-chat-window { position: fixed; bottom: 85px; right: 50%; transform: translateX(50%); width: 95%; max-width: 440px; height: 500px; max-height: calc(100vh - 120px); background: #fff; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); z-index: 3000; display: none; flex-direction: column; overflow: hidden; border: 1px solid #eee; }
            .ai-header { background: #111; color: #fff; padding: 15px; font-weight: 700; display: flex; justify-content: space-between; align-items: center; }
            .ai-close { background: none; border: none; color: #fff; font-size: 24px; cursor: pointer; display: flex; align-items: center; justify-content: center; padding: 0; width: 24px; height: 24px; }
            .ai-messages { flex-grow: 1; padding: 15px; overflow-y: auto; background: #f8f9fa; display: flex; flex-direction: column; gap: 12px; scroll-behavior: smooth; }
            .msg-bubble { max-width: 85%; padding: 12px 16px; border-radius: 14px; font-size: 0.85rem; line-height: 1.5; word-wrap: break-word; }
            .msg-kimi { background: #fff; border: 1px solid #eee; align-self: flex-start; border-bottom-left-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
            .msg-user { background: var(--pizz-green, #2ecc71); color: #fff; align-self: flex-end; border-bottom-right-radius: 4px; box-shadow: 0 2px 5px rgba(46,204,113,0.2); }
            .ai-input-area { padding: 12px; background: #fff; border-top: 1px solid #eee; display: flex; gap: 8px; align-items: center; }
            .ai-input { flex-grow: 1; border: 1px solid #ddd; border-radius: 20px; padding: 12px 15px; font-size: 0.85rem; outline: none; font-family: inherit; transition: border-color 0.2s; }
            .ai-input:focus { border-color: var(--pizz-green, #2ecc71); }
            .ai-btn { background: #f0f2f5; border: none; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #2c3e50; transition: 0.2s; flex-shrink: 0; }
            .ai-btn:hover { background: #e0e4e8; }
            .ai-btn-send { background: var(--pizz-green, #2ecc71); color: #fff; }
            .ai-btn-send:hover { background: #27ae60; }
            .ai-qr-box { background: #fff; padding: 15px; border-radius: 12px; border: 2px dashed #2ecc71; text-align: center; margin-top: 5px; }
            .ai-qr-box img { width: 150px; height: 150px; border-radius: 8px; margin-top: 10px; }
            .typing-indicator { font-weight: bold; color: #7f8c8d; animation: blink 1.4s infinite both; }
            @keyframes blink { 0% { opacity: .2; } 20% { opacity: 1; } 100% { opacity: .2; } }
        `;
        document.head.appendChild(style);
    },

    injectHTML: function() {
        const html = `
            <div id="ai-chat-window">
                <div class="ai-header">
                    <span style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.2rem;">🤖</span> ជំនួយការ Kimi 
                    </span>
                    <button class="ai-close" onclick="AIChatEngine.toggleChat()">×</button>
                </div>
                
                <div class="ai-messages" id="ai-msg-container">
                    <div class="msg-bubble msg-kimi">សួស្តី! ខ្ញុំជាជំនួយការ Kimi របស់ Pizza King។ តើមានអ្វីឱ្យខ្ញុំជួយទេថ្ងៃនេះ? (I can help you order, check stock, or verify payments!)</div>
                </div>
                
                <div class="ai-input-area">
                    <button class="ai-btn" onclick="document.getElementById('ai-file-upload').click()">
                        <svg viewBox="0 0 24 24" style="width: 20px; height: 20px; fill: currentColor;"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>
                    </button>
                    <input type="file" id="ai-file-upload" style="display: none;" accept="image/*">

                    <input type="text" class="ai-input" id="ai-text-input" placeholder="សរសេរសារទីនេះ... (Type here...)">
                    
                    <button class="ai-btn ai-btn-send" onclick="AIChatEngine.sendMessage()">
                        <svg viewBox="0 0 24 24" style="width: 18px; height: 18px; fill: currentColor;"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                    </button>
                </div>
            </div>
        `;
        const wrapper = document.createElement('div');
        wrapper.innerHTML = html;
        document.body.appendChild(wrapper);
    },

    attachListeners: function() {
        const input = document.getElementById('ai-text-input');
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') AIChatEngine.sendMessage();
        });
        
        // File Upload Handler (For Bank Slips)
        document.getElementById('ai-file-upload').addEventListener('change', function(e) {
            if(e.target.files.length > 0) {
                AIChatEngine.appendMessage("user", "📸 បង្ហោះវិក័យប័ត្របញ្ជាក់ការបង់ប្រាក់ (Payment Slip Uploaded)");
                AIChatEngine.sendMessage("I just uploaded my payment slip image to verify my transfer.");
                e.target.value = ""; // Reset input
            }
        });
    },

    toggleChat: function() {
        const win = document.getElementById('ai-chat-window');
        win.style.display = win.style.display === 'flex' ? 'none' : 'flex';
        if (win.style.display === 'flex') {
            document.getElementById('ai-text-input').focus();
        }
    },

    appendMessage: function(sender, text, isHTML = false) {
        const container = document.getElementById('ai-msg-container');
        const div = document.createElement('div');
        div.className = `msg-bubble msg-${sender}`;
        
        if (isHTML) {
            div.innerHTML = text;
        } else {
            div.innerHTML = text.replace(/\\n/g, '<br>');
        }
        
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
        return div; 
    },

    sendMessage: async function(overrideText = null) {
        const input = document.getElementById('ai-text-input');
        const text = overrideText || input.value.trim();
        if (!text) return;

        if (!overrideText) this.appendMessage("user", text);
        input.value = '';

        this.chatHistory.push({ role: "user", content: text });

        const typingIndicator = this.appendMessage("kimi", "<span class='typing-indicator'>... កំពុងគិត ...</span>", true);

        try {
            const response = await fetch(`${APP_CONFIG.RENDER_URL}/ai-chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: text,
                    history: this.chatHistory 
                })
            });

            if (!response.ok) throw new Error("Server disconnected");

            const data = await response.json();
            typingIndicator.remove();

            if (data.reply) {
                this.appendMessage("kimi", data.reply);
                this.chatHistory.push({ role: "assistant", content: data.reply });
            }

            if (data.action === "show_qr" && data.checkout_data) {
                this.renderChatQR(data.checkout_data.total);
            }

        } catch (e) {
            console.error("AI Error:", e);
            typingIndicator.remove();
            this.appendMessage("kimi", "⚠️ សុំទោស ប្រព័ន្ធមានបញ្ហាបន្តិចបន្តួច។ សូមព្យាយាមម្តងទៀត។ (Network error, please try again.)");
        }
    },

    renderChatQR: function(totalAmount) {
        if (typeof generateDynamicABAQR !== 'function') {
            console.error("aba-qr.js is missing!");
            return;
        }

        const dynamicQR = generateDynamicABAQR(totalAmount);
        const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(dynamicQR)}`;
        
        const qrHTML = `
            <div class="ai-qr-box">
                <div style="font-weight:700; color:#e74c3c;">បង់ប្រាក់សរុប: ${totalAmount.toLocaleString()}៛</div>
                <img src="${qrUrl}" alt="ABA QR Code">
                <div style="font-size:0.75rem; margin-top:5px; color:#7f8c8d;">សូមស្កេនដើម្បីទូទាត់ (Scan to pay)</div>
            </div>
        `;
        
        this.appendMessage("kimi", qrHTML, true);
    }
};

document.addEventListener('DOMContentLoaded', () => AIChatEngine.init());
