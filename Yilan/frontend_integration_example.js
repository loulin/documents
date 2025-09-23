/**
 * 前端集成示例
 * 展示如何在Web应用中调用健康顾问API
 */

class HealthAdvisorClient {
    constructor(apiBaseUrl = 'http://localhost:8000') {
        this.apiBaseUrl = apiBaseUrl;
        this.currentUserId = this.getCurrentUserId();
        this.userProfile = null;
        
        // 初始化时加载用户档案
        this.loadUserProfile();
    }
    
    /**
     * 获取当前用户ID（实际应用中从登录状态获取）
     */
    getCurrentUserId() {
        // 实际应用中应该从认证系统获取
        return localStorage.getItem('user_id') || 'demo_user';
    }
    
    /**
     * 发送健康咨询消息
     */
    async sendHealthQuery(message) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    user_id: this.currentUserId,
                    user_profile: this.userProfile
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            // 显示处理信息（调试用）
            if (result.knowledge_used && result.knowledge_used.length > 0) {
                console.log('🔍 使用的知识库:', result.knowledge_used);
            }
            if (result.rules_applied > 0) {
                console.log('⚙️ 应用的个性化规则数量:', result.rules_applied);
            }
            
            return result;
            
        } catch (error) {
            console.error('❌ 发送健康咨询时出错:', error);
            return {
                status: 'error',
                response: '抱歉，服务暂时不可用，请稍后重试。',
                type: 'error'
            };
        }
    }
    
    /**
     * 更新用户档案
     */
    async updateUserProfile(profileData) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/user/profile`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.currentUserId,
                    ...profileData
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            this.userProfile = result.user_profile;
            
            console.log('✅ 用户档案更新成功');
            return result;
            
        } catch (error) {
            console.error('❌ 更新用户档案时出错:', error);
            return { status: 'error', message: '更新失败' };
        }
    }
    
    /**
     * 加载用户档案
     */
    async loadUserProfile() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/user/${this.currentUserId}/profile`);
            
            if (response.status === 404) {
                // 用户档案不存在，创建默认档案
                console.log('📝 用户档案不存在，创建默认档案');
                return;
            }
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            this.userProfile = result.user_profile;
            
            console.log('📋 用户档案加载成功:', this.userProfile);
            
        } catch (error) {
            console.error('❌ 加载用户档案时出错:', error);
        }
    }
    
    /**
     * 获取知识库统计信息
     */
    async getKnowledgeStats() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/knowledge/stats`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('📊 知识库统计:', result);
            return result;
            
        } catch (error) {
            console.error('❌ 获取知识库统计时出错:', error);
            return null;
        }
    }
    
    /**
     * 检查服务健康状态
     */
    async checkHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            const result = await response.json();
            return result.status === 'healthy';
        } catch (error) {
            console.error('❌ 健康检查失败:', error);
            return false;
        }
    }
}

/**
 * 聊天界面类
 */
class ChatInterface {
    constructor() {
        this.client = new HealthAdvisorClient();
        this.chatContainer = null;
        this.messageInput = null;
        this.sendButton = null;
        
        this.init();
    }
    
    /**
     * 初始化界面
     */
    init() {
        // 创建聊天界面DOM
        this.createChatInterface();
        
        // 绑定事件
        this.bindEvents();
        
        // 显示欢迎消息
        this.showWelcomeMessage();
        
        // 检查服务状态
        this.checkServiceStatus();
    }
    
    /**
     * 创建聊天界面
     */
    createChatInterface() {
        const chatHtml = `
            <div id="health-advisor-chat" style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div id="chat-header" style="background: #f0f8ff; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="margin: 0; color: #2c5aa0;">🏥 健康顾问助手</h2>
                    <p style="margin: 5px 0 0 0; color: #666;">专业的糖尿病健康咨询服务</p>
                </div>
                
                <div id="chat-messages" style="height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; background: white; border-radius: 8px;"></div>
                
                <div id="chat-input" style="display: flex; gap: 10px;">
                    <input type="text" id="message-input" placeholder="输入您的健康问题..." 
                           style="flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;">
                    <button id="send-button" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        发送
                    </button>
                </div>
                
                <div id="service-status" style="margin-top: 10px; padding: 8px; text-align: center; font-size: 12px; border-radius: 4px;">
                    <span id="status-indicator">🔄 检查服务状态中...</span>
                </div>
                
                <div id="example-questions" style="margin-top: 15px;">
                    <p style="margin: 10px 0 5px 0; font-size: 12px; color: #666;">示例问题：</p>
                    <div style="display: flex; flex-wrap: wrap; gap: 5px;">
                        <button class="example-btn" data-message="头晕了">头晕了</button>
                        <button class="example-btn" data-message="忘记吃药了">忘记吃药了</button>
                        <button class="example-btn" data-message="睡不着">睡不着</button>
                        <button class="example-btn" data-message="刚运动完">刚运动完</button>
                        <button class="example-btn" data-message="起床了">起床了</button>
                    </div>
                </div>
            </div>
        `;
        
        // 插入到页面中
        document.body.innerHTML = chatHtml;
        
        // 获取DOM元素引用
        this.chatContainer = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        
        // 示例按钮样式
        const style = document.createElement('style');
        style.textContent = `
            .example-btn {
                padding: 5px 10px;
                background: #e9ecef;
                border: 1px solid #dee2e6;
                border-radius: 15px;
                font-size: 12px;
                cursor: pointer;
                transition: background-color 0.2s;
            }
            .example-btn:hover {
                background: #d6d8db;
            }
        `;
        document.head.appendChild(style);
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        // 发送按钮点击事件
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // 输入框回车事件
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        // 示例问题按钮点击事件
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const message = e.target.getAttribute('data-message');
                this.messageInput.value = message;
                this.sendMessage();
            });
        });
    }
    
    /**
     * 发送消息
     */
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // 显示用户消息
        this.addMessage('user', message);
        
        // 清空输入框并显示加载状态
        this.messageInput.value = '';
        this.sendButton.disabled = true;
        this.sendButton.textContent = '处理中...';
        
        try {
            // 调用API
            const result = await this.client.sendHealthQuery(message);
            
            // 显示AI回复
            this.addMessage('ai', result.response, result);
            
        } catch (error) {
            this.addMessage('ai', '抱歉，处理您的问题时出现了错误，请稍后重试。');
        } finally {
            // 恢复发送按钮状态
            this.sendButton.disabled = false;
            this.sendButton.textContent = '发送';
            this.messageInput.focus();
        }
    }
    
    /**
     * 添加消息到聊天界面
     */
    addMessage(sender, content, metadata = null) {
        const messageDiv = document.createElement('div');
        messageDiv.style.marginBottom = '15px';
        
        const senderName = sender === 'user' ? '您' : '🏥 健康顾问';
        const senderColor = sender === 'user' ? '#007bff' : '#28a745';
        const alignment = sender === 'user' ? 'right' : 'left';
        
        let metadataHtml = '';
        if (metadata && sender === 'ai') {
            const details = [];
            if (metadata.knowledge_used && metadata.knowledge_used.length > 0) {
                details.push(`📚 知识库: ${metadata.knowledge_used.join(', ')}`);
            }
            if (metadata.rules_applied > 0) {
                details.push(`⚙️ 个性化规则: ${metadata.rules_applied}条`);
            }
            if (details.length > 0) {
                metadataHtml = `<div style="font-size: 11px; color: #666; margin-top: 5px;">${details.join(' | ')}</div>`;
            }
        }
        
        messageDiv.innerHTML = `
            <div style="text-align: ${alignment};">
                <div style="display: inline-block; max-width: 80%; text-align: left;">
                    <div style="color: ${senderColor}; font-weight: bold; font-size: 12px; margin-bottom: 3px;">
                        ${senderName}
                    </div>
                    <div style="background: ${sender === 'user' ? '#e3f2fd' : '#f8f9fa'}; 
                                padding: 10px; 
                                border-radius: 8px; 
                                white-space: pre-wrap; 
                                line-height: 1.4;">
                        ${content}
                    </div>
                    ${metadataHtml}
                </div>
            </div>
        `;
        
        this.chatContainer.appendChild(messageDiv);
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }
    
    /**
     * 显示欢迎消息
     */
    showWelcomeMessage() {
        const welcomeMessage = `欢迎使用健康顾问助手！🎉

我是您的专业健康顾问，可以帮助您：
• 🩺 分析身体症状和健康问题
• 💊 提供用药指导和管理建议  
• 🍽️ 进行食物营养分析和饮食建议
• 🏃‍♀️ 制定个性化运动方案
• 🌙 给出睡眠改善建议
• 📊 血糖管理和监测指导

请放心咨询任何健康相关的问题，我会根据您的具体情况提供专业建议。

您可以点击下方的示例问题开始体验，或者直接输入您的问题。`;

        this.addMessage('ai', welcomeMessage);
    }
    
    /**
     * 检查服务状态
     */
    async checkServiceStatus() {
        const statusIndicator = document.getElementById('status-indicator');
        
        try {
            const isHealthy = await this.client.checkHealth();
            
            if (isHealthy) {
                statusIndicator.innerHTML = '✅ 服务正常运行';
                statusIndicator.parentElement.style.background = '#d4edda';
                statusIndicator.parentElement.style.color = '#155724';
                
                // 获取知识库统计
                const stats = await this.client.getKnowledgeStats();
                if (stats) {
                    const kbCount = Object.keys(stats.knowledge_bases).length;
                    statusIndicator.innerHTML += ` | 📚 已加载${kbCount}个知识库`;
                }
            } else {
                statusIndicator.innerHTML = '❌ 服务连接失败';
                statusIndicator.parentElement.style.background = '#f8d7da';
                statusIndicator.parentElement.style.color = '#721c24';
            }
        } catch (error) {
            statusIndicator.innerHTML = '⚠️ 无法连接到服务';
            statusIndicator.parentElement.style.background = '#fff3cd';
            statusIndicator.parentElement.style.color = '#856404';
        }
    }
}

// 页面加载完成后初始化聊天界面
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 健康顾问前端界面初始化...');
    
    // 创建聊天界面
    window.healthAdvisorChat = new ChatInterface();
    
    // 全局暴露客户端实例（用于调试）
    window.healthAdvisorClient = window.healthAdvisorChat.client;
    
    console.log('✅ 界面初始化完成');
});

// 导出类（如果使用模块化）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { HealthAdvisorClient, ChatInterface };
}