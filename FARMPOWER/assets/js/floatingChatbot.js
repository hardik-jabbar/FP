// Floating Chatbot injected on every page
// Author: Cascade AI assistant
(function() {
  // Prevent multiple injections
  if (document.getElementById('ai-chat-button')) return;

  // Helper to create element with classes and attributes
  function el(tag, attrs = {}, innerHTML = '') {
    const e = document.createElement(tag);
    Object.entries(attrs).forEach(([k, v]) => {
      if (k === 'class') e.className = v;
      else if (k === 'id') e.id = v;
      else e.setAttribute(k, v);
    });
    if (innerHTML) e.innerHTML = innerHTML;
    return e;
  }

  // Chat Icon Button (bottom-right)
  const chatBtn = el('button', {
    id: 'ai-chat-button',
    class: 'fixed bottom-4 right-4 md:bottom-6 md:right-6 bg-primary text-primary-foreground p-4 rounded-full shadow-lg hover:bg-primary/90 transition-all duration-200 z-50 flex items-center justify-center',
    'aria-label': 'Open AI Chat',
    style: 'width: 56px; height: 56px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);'
  });
  chatBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>';

  // Modal overlay
  const modalOverlay = el('div', {
    id: 'ai-chat-modal',
    class: 'fixed inset-0 bg-black/50 hidden z-50',
    style: 'backdrop-filter: blur(4px);'
  });

  // Modal content container
  const modal = el('div', {
    class: 'fixed inset-4 md:inset-auto md:bottom-6 md:right-6 md:top-auto md:w-[400px] md:max-h-[calc(100vh-3rem)] bg-background border border-border rounded-xl shadow-2xl flex flex-col z-50',
    style: 'max-height: calc(100vh - 2rem);'
  });

  // Header
  const header = el('div', { 
    class: 'flex items-center justify-between p-4 border-b border-border bg-secondary/50' 
  });
  header.innerHTML = `
    <div class="flex items-center space-x-3">
      <div class="bg-primary/10 p-2 rounded-lg">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
      </div>
      <h3 class="text-lg font-semibold">Farming Assistant</h3>
    </div>`;
  
  const closeBtn = el('button', { 
    id: 'close-chat', 
    class: 'p-1.5 hover:bg-muted rounded-lg transition-colors',
    'aria-label': 'Close chat'
  });
  closeBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"></path></svg>';
  header.appendChild(closeBtn);
  modal.appendChild(header);

  // Chat window container
  const chatWindow = el('div', { 
    id: 'chat-window-main',
    class: 'flex-1 overflow-y-auto p-4 space-y-4',
    style: 'min-height: 0;' // Critical for flex item sizing
  });
  
  // Initial welcome message
  const welcomeMsg = el('div', { class: 'flex justify-start' });
  welcomeMsg.innerHTML = `
    <div class="bg-muted text-foreground p-4 rounded-2xl rounded-tl-sm max-w-[85%] md:max-w-[75%]">
      <p>Hello! I'm your AI Farming Assistant. I can help with:</p>
      <ul class="list-disc pl-5 mt-2 space-y-1 text-sm text-muted-foreground">
        <li>Crop advice</li>
        <li>Soil health</li>
        <li>Pest control</li>
        <li>Weather impacts</li>
      </ul>
      <p class="mt-2 text-sm">How can I help you today?</p>
    </div>`;
  chatWindow.appendChild(welcomeMsg);
  modal.appendChild(chatWindow);

  // Input area
  const inputBar = el('div', { 
    class: 'border-t border-border p-3 bg-background/80 backdrop-blur-sm',
    style: 'flex-shrink: 0;'
  });
  
  const inputContainer = el('div', {
    class: 'flex items-center gap-2 bg-background border border-border rounded-xl px-3 focus-within:ring-2 focus-within:ring-primary/50 transition-all'
  });
  
  const userInput = el('input', { 
    type: 'text', 
    id: 'user-input', 
    class: 'flex-1 py-3 bg-transparent outline-none text-sm md:text-base placeholder:text-muted-foreground/60', 
    placeholder: 'Ask me anything about farming...',
    'aria-label': 'Type your message',
    style: 'min-width: 0;' // Prevents input from overflowing
  });
  
  const sendBtn = el('button', { 
    id: 'send-button', 
    class: 'p-2 text-primary hover:bg-primary/10 rounded-lg transition-colors disabled:opacity-50 disabled:pointer-events-none',
    'aria-label': 'Send message',
    disabled: true
  });
  sendBtn.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M22 2L11 13"></path>
      <path d="M22 2l-7 20-4-9-9-4 20-7z"></path>
    </svg>`;
  
  inputContainer.appendChild(userInput);
  inputContainer.appendChild(sendBtn);
  inputBar.appendChild(inputContainer);
  modal.appendChild(inputBar);

  // Add elements to the DOM
  modalOverlay.appendChild(modal);
  document.body.appendChild(chatBtn);
  document.body.appendChild(modalOverlay);

  // Session management
  let sessionId = localStorage.getItem('farmpower_chat_session_id');
  if (!sessionId) {
    sessionId = 'temp-' + Date.now();
    localStorage.setItem('farmpower_chat_session_id', sessionId);
  }

  // Functions
  function appendMessage(sender, message) {
    const msgDiv = el('div', { 
      class: `flex ${sender === 'user' ? 'justify-end' : 'justify-start'}` 
    });
    
    const messageClasses = [
      'px-4 py-3 rounded-2xl',
      'break-words',
      'max-w-[85%] md:max-w-[75%]',
      'text-sm md:text-base',
      sender === 'user' 
        ? 'bg-primary text-primary-foreground rounded-br-sm' 
        : 'bg-muted text-foreground rounded-tl-sm'
    ].join(' ');
    
    // Convert markdown links to HTML
    const processedMessage = message.replace(
      /\[([^\]]+)\]\(([^)]+)\)/g, 
      '<a href="$2" target="_blank" class="text-primary underline hover:text-primary/80">$1</a>'
    );
    
    msgDiv.innerHTML = `<div class="${messageClasses}">${processedMessage}</div>`;
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  async function sendMessage() {
    const query = userInput.value.trim();
    if (!query) return;
    
    // Add user message
    appendMessage('user', query);
    userInput.value = '';
    updateSendButton();
    
    // Show typing indicator
    const typingIndicator = el('div', { class: 'flex justify-start' });
    typingIndicator.innerHTML = `
      <div class="bg-muted text-foreground p-4 rounded-2xl rounded-tl-sm max-w-[85%] md:max-w-[75%] flex space-x-2">
        <div class="w-2 h-2 rounded-full bg-muted-foreground animate-bounce"></div>
        <div class="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style="animation-delay: 0.2s"></div>
        <div class="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style="animation-delay: 0.4s"></div>
      </div>`;
    chatWindow.appendChild(typingIndicator);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query,
          sessionId: sessionId
        })
      });
      
      // Remove typing indicator
      chatWindow.removeChild(typingIndicator);
      
      if (response.ok) {
        const data = await response.json();
        // Update session ID if a new one was generated
        if (data.sessionId && data.sessionId !== sessionId) {
          sessionId = data.sessionId;
          localStorage.setItem('farmpower_chat_session_id', sessionId);
        }
        appendMessage('ai', data.response);
      } else {
        const error = await response.json().catch(() => ({}));
        appendMessage('ai', `Sorry, I encountered an error: ${error.message || 'Please try again later.'}`);
      }
    } catch (err) {
      console.error('AI chat error:', err);
      chatWindow.removeChild(typingIndicator);
      appendMessage('ai', 'I\'m having trouble connecting right now. Please try again in a moment.');
    }
  }
  
  function updateSendButton() {
    const hasText = userInput.value.trim().length > 0;
    sendBtn.disabled = !hasText;
    sendBtn.classList.toggle('text-primary', hasText);
    sendBtn.classList.toggle('text-muted-foreground', !hasText);
  }

  // Event listeners
  chatBtn.addEventListener('click', () => {
    modalOverlay.classList.remove('hidden');
    chatBtn.classList.add('hidden');
    userInput.focus();
  });
  
  closeBtn.addEventListener('click', () => {
    modalOverlay.classList.add('hidden');
    chatBtn.classList.remove('hidden');
  });
  
  modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) {
      modalOverlay.classList.add('hidden');
      chatBtn.classList.remove('hidden');
    }
  });
  
  sendBtn.addEventListener('click', sendMessage);
  
  userInput.addEventListener('input', updateSendButton);
  
  userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (userInput.value.trim()) {
        sendMessage();
      }
    }
  });
  
  // Initial update for send button state
  updateSendButton();
})();
