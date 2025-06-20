// chatClient.js - Frontend client for AI chat functionality

class ChatClient {
  constructor(options = {}) {
    this.baseUrl = options.baseUrl || '/api';
    this.sessionId = options.sessionId || null;
    this.onMessage = options.onMessage || (() => {});
    this.onError = options.onError || console.error;
    this.onSessionUpdate = options.onSessionUpdate || (() => {});
    this.headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };
    
    // Initialize session from storage if available
    this._loadSession();
  }
  
  /**
   * Load session from localStorage if available
   * @private
   */
  _loadSession() {
    try {
      const savedSession = localStorage.getItem('aiChatSession');
      if (savedSession) {
        const { sessionId, timestamp } = JSON.parse(savedSession);
        // Only use session if it's less than 24 hours old
        if (Date.now() - timestamp < 24 * 60 * 60 * 1000) {
          this.sessionId = sessionId;
          this.onSessionUpdate({ sessionId });
        } else {
          this._clearSession();
        }
      }
    } catch (error) {
      console.warn('Failed to load chat session:', error);
      this._clearSession();
    }
  }
  
  /**
   * Save session to localStorage
   * @private
   */
  _saveSession() {
    if (this.sessionId) {
      try {
        localStorage.setItem('aiChatSession', JSON.stringify({
          sessionId: this.sessionId,
          timestamp: Date.now()
        }));
      } catch (error) {
        console.warn('Failed to save chat session:', error);
      }
    }
  }
  
  /**
   * Clear the current session
   * @private
   */
  _clearSession() {
    this.sessionId = null;
    try {
      localStorage.removeItem('aiChatSession');
    } catch (error) {
      console.warn('Failed to clear chat session:', error);
    }
    this.onSessionUpdate({ sessionId: null });
  }
  
  /**
   * Send a message to the AI chat
   * @param {string} message - The user's message
   * @returns {Promise<Object>} - The AI's response
   */
  async sendMessage(message) {
    if (!message || typeof message !== 'string' || message.trim().length === 0) {
      throw new Error('Message must be a non-empty string');
    }
    
    try {
      const response = await fetch(`${this.baseUrl}/chat`, {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify({
          query: message,
          sessionId: this.sessionId
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Update session if a new one was created
      if (data.sessionId && data.sessionId !== this.sessionId) {
        this.sessionId = data.sessionId;
        this._saveSession();
        this.onSessionUpdate({ sessionId: this.sessionId });
      }
      
      // Call the message handler
      this.onMessage({
        type: 'ai',
        content: data.response,
        timestamp: new Date().toISOString()
      });
      
      return data;
      
    } catch (error) {
      this.onError({
        type: 'error',
        message: error.message || 'Failed to send message',
        timestamp: new Date().toISOString()
      });
      throw error;
    }
  }
  
  /**
   * Clear the current chat session
   */
  clearSession() {
    this._clearSession();
  }
  
  /**
   * Check if the chat service is available
   * @returns {Promise<boolean>} - Whether the service is available
   */
  async checkHealth() {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: this.headers
      });
      
      if (!response.ok) return false;
      
      const data = await response.json();
      return data.status === 'ok';
      
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }
}

// Export as both default and named export
export { ChatClient };
export default ChatClient;
