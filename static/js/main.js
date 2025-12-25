// 聊天功能的前端逻辑
class ChatApp {
    constructor() {
        this.sessionId = window.SESSION_ID || this.generateSessionId();
        this.messageInput = document.getElementById('message-input');
        this.sendBtn = document.getElementById('send-btn');
        this.chatMessages = document.getElementById('chat-messages');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.clearBtn = document.getElementById('clear-btn');
        
        this.initEventListeners();
        this.autoResizeTextarea();
    }
    
    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9);
    }
    
    initEventListeners() {
        // 发送按钮点击事件
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        
        // 回车键发送消息，Shift+Enter换行
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // 清空上下文按钮点击事件
        this.clearBtn.addEventListener('click', () => this.clearContext());
        
        // 自动调整输入框高度
        this.messageInput.addEventListener('input', () => this.autoResizeTextarea());
    }
    
    autoResizeTextarea() {
        const textarea = this.messageInput;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // 添加用户消息到聊天界面
        this.addMessageToUI(message, 'user');
        
        // 清空输入框
        this.messageInput.value = '';
        this.autoResizeTextarea();
        
        // 显示输入指示器
        this.showTypingIndicator();
        
        try {
            // 发送请求到后端
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    message: message
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // 添加机器人回复到聊天界面
                this.addMessageToUI(data.response, 'bot', data.ref_info);
            } else {
                this.addMessageToUI('抱歉，出现了错误：' + data.error, 'bot');
            }
        } catch (error) {
            console.error('聊天请求失败:', error);
            this.addMessageToUI('抱歉，连接服务器失败，请稍后重试。', 'bot');
        } finally {
            // 隐藏输入指示器
            this.hideTypingIndicator();
        }
    }
    
    addMessageToUI(content, type, refInfo = []) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // 将文本内容转换为HTML，处理换行
        const formattedContent = content.replace(/\n/g, '<br>');
        contentDiv.innerHTML = `<p>${formattedContent}</p>`;
        
        // 添加参考信息
        if (refInfo && refInfo.length > 0) {
            const refDiv = document.createElement('div');
            refDiv.className = 'ref-info';
            refDiv.innerHTML = '<h4>参考信息：</h4><ul>';
            
            refInfo.forEach(info => {
                if (info && info.urls) {
                    info.urls.forEach(url => {
                        refDiv.innerHTML += `<li><a href="${url}" target="_blank">${url}</a></li>`;
                    });
                }
            });
            
            refDiv.innerHTML += '</ul>';
            contentDiv.appendChild(refDiv);
        }
        
        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);
        
        // 滚动到底部
        this.scrollToBottom();
    }
    
    showTypingIndicator() {
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    async clearContext() {
        try {
            await fetch('/api/clear_context', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId
                })
            });
            
            // 清空聊天界面
            this.chatMessages.innerHTML = '';
            this.addMessageToUI('上下文已清空，我们可以开始新的对话了！', 'bot');
        } catch (error) {
            console.error('清空上下文失败:', error);
            this.addMessageToUI('抱歉，清空上下文失败，请稍后重试。', 'bot');
        }
    }
}

// 页面加载完成后初始化聊天应用
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});
