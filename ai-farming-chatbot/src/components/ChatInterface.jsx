import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../contexts/ChatContext';
import { FiSend, FiTrash2, FiThumbsUp, FiThumbsDown } from 'react-icons/fi';

const ChatInterface = () => {
  const {
    messages,
    isTyping,
    error,
    sendMessage,
    clearChat,
    sendFeedback,
  } = useChat();
  
  const [input, setInput] = useState('');
  const [suggestions] = useState([
    'What are the best crops for my region?',
    'How do I prepare soil for planting?',
    'What are common pests for tomatoes?',
    'How often should I water my plants?',
  ]);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  
  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  // Focus input on component mount
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isTyping) return;
    
    const message = input.trim();
    setInput('');
    
    try {
      await sendMessage(message);
    } catch (err) {
      console.error('Error sending message:', err);
    }
  };
  
  const handleSuggestionClick = async (suggestion) => {
    setInput(suggestion);
    inputRef.current.focus();
  };
  
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };
  
  const renderMessage = (message) => {
    const isUser = message.role === 'user';
    const messageClass = isUser 
      ? 'bg-blue-100 text-blue-900 self-end rounded-l-lg rounded-tr-lg'
      : 'bg-gray-100 text-gray-900 self-start rounded-r-lg rounded-tl-lg';
    
    return (
      <div 
        key={message.id} 
        className={`max-w-3/4 p-3 my-1 ${messageClass} shadow-sm`}
      >
        <div className="whitespace-pre-wrap">{message.content}</div>
        <div className="flex items-center justify-between mt-1 text-xs opacity-70">
          <span>
            {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
          {!isUser && (
            <div className="flex space-x-1">
              <button 
                onClick={() => sendFeedback(message.id, 1)}
                className="p-1 rounded-full hover:bg-white/20"
                aria-label="Helpful"
              >
                <FiThumbsUp className="w-3.5 h-3.5" />
              </button>
              <button 
                onClick={() => sendFeedback(message.id, 0, 'Not helpful')}
                className="p-1 rounded-full hover:bg-white/20"
                aria-label="Not helpful"
              >
                <FiThumbsDown className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>
      </div>
    );
  };
  
  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4 flex justify-between items-center">
        <h2 className="text-lg font-semibold text-gray-800">Farming Assistant</h2>
        <button
          onClick={clearChat}
          className="text-sm text-red-600 hover:text-red-800 flex items-center"
          disabled={messages.length === 0}
        >
          <FiTrash2 className="mr-1" /> Clear Chat
        </button>
      </div>
      
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-8 text-gray-500">
            <div className="bg-white p-6 rounded-xl shadow-sm max-w-md w-full">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Welcome to Farming Assistant</h3>
              <p className="mb-4">Ask me anything about farming, crops, livestock, or agricultural practices.</p>
              
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-700">Try asking:</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="text-sm text-left p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          messages.map(renderMessage)
        )}
        
        {isTyping && (
          <div className="flex items-center space-x-2 p-3 bg-gray-100 rounded-lg self-start max-w-xs">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        )}
        
        {error && (
          <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input */}
      <div className="border-t border-gray-200 p-4 bg-white">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              className="w-full p-3 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:outline-none"
              disabled={isTyping}
            />
            <button
              type="button"
              onClick={handleSubmit}
              disabled={!input.trim() || isTyping}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 text-gray-500 hover:text-blue-600 disabled:opacity-50"
              aria-label="Send message"
            >
              <FiSend className="w-5 h-5" />
            </button>
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isTyping}
            className="px-6 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-colors flex items-center justify-center"
          >
            <span className="hidden sm:inline">Send</span>
            <FiSend className="w-5 h-5 sm:ml-2" />
          </button>
        </form>
        
        <p className="text-xs text-gray-500 mt-2 text-center">
          FarmAI Assistant may produce inaccurate information. Always verify critical information.
        </p>
      </div>
    </div>
  );
};

export default ChatInterface;
