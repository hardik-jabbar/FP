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
    class: 'fixed bottom-6 right-6 bg-primary text-primary-foreground p-4 rounded-full shadow-lg hover:bg-primary/90 transition-all duration-200 z-50'
  });
  chatBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>';

  // Modal overlay
  const modalOverlay = el('div', {
    id: 'ai-chat-modal',
    class: 'fixed inset-0 bg-black/50 hidden z-50'
  });

  // Modal content container
  const modal = el('div', {
    class: 'absolute bottom-6 right-6 w-96 h-[500px] bg-secondary border border-border rounded-lg shadow-lg flex flex-col'
  });

  // Header
  const header = el('div', { class: 'flex items-center justify-between p-4 border-b border-border' });
  header.innerHTML = '<h3 class="text-lg font-medium">AI Farming Assistant</h3>';
  const closeBtn = el('button', { id: 'close-chat', class: 'p-2 hover:bg-background rounded-lg' });
  closeBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"></path></svg>';
  header.appendChild(closeBtn);
  modal.appendChild(header);

  // Chat window
  const chatWindow = el('div', { id: 'chat-window-modal', class: 'flex-1 p-4 overflow-y-auto space-y-4' });
  chatWindow.innerHTML = '<div class="flex justify-start"><div class="bg-muted text-muted-foreground p-3 rounded-lg max-w-[70%]">Hello! I am your AI Farming Assistant. How can I help you today?</div></div>';
  modal.appendChild(chatWindow);

  // Input area
  const inputBar = el('div', { class: 'border-t border-border p-4 flex items-center space-x-4' });
  const userInput = el('input', { type: 'text', id: 'user-input', class: 'flex-1 p-3 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-2 focus:ring-primary', placeholder: 'Type your message...' });
  const sendBtn = el('button', { id: 'send-button', class: 'inline-flex items-center justify-center rounded-lg bg-primary px-5 py-3 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90' }, 'Send');
  sendBtn.textContent = 'Send';
  inputBar.appendChild(userInput);
  inputBar.appendChild(sendBtn);
  modal.appendChild(inputBar);

  modalOverlay.appendChild(modal);
  document.body.appendChild(chatBtn);
  document.body.appendChild(modalOverlay);

  // Functions
  function appendMessage(sender, message) {
    const msgDiv = el('div', { class: 'flex ' + (sender === 'user' ? 'justify-end' : 'justify-start') });
    msgDiv.innerHTML = `<div class="${sender === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'} p-3 rounded-lg max-w-[70%]">${message}</div>`;
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  async function sendMessage() {
    const query = userInput.value.trim();
    if (!query) return;
    appendMessage('user', query);
    userInput.value = '';
    try {
      const response = await fetch('http://localhost:3000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      const data = await response.json();
      if (response.ok) {
        appendMessage('ai', data.response);
      } else {
        appendMessage('ai', `Error: ${data.error || 'Something went wrong.'}`);
      }
    } catch (err) {
      console.error('AI chat error', err);
      appendMessage('ai', 'Error: Could not connect to the AI service.');
    }
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
  userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
  });
})();
