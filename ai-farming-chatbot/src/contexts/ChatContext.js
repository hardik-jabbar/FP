import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import chatService from '../services/chatService';
import { v4 as uuidv4 } from 'uuid';

// Create the context
const ChatContext = createContext();

// Custom hook to use the chat context
export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

// Provider component
export const ChatProvider = ({ children }) => {
  // State for chat messages
  const [messages, setMessages] = useState([]);
  
  // State for the current session
  const [sessionId, setSessionId] = useState(() => {
    // Try to load session ID from localStorage
    const savedSession = localStorage.getItem('chatSession');
    return savedSession ? JSON.parse(savedSession).sessionId : null;
  });
  
  // State for loading and error states
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  
  // Load chat history when session ID changes
  useEffect(() => {
    const loadChatHistory = async () => {
      if (!sessionId) return;
      
      try {
        setIsLoading(true);
        const history = await chatService.getChatHistory(sessionId);
        if (history && history.length > 0) {
          setMessages(history);
        }
      } catch (err) {
        console.error('Failed to load chat history:', err);
        setError('Failed to load chat history');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadChatHistory();
  }, [sessionId]);
  
  // Save session ID to localStorage when it changes
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem('chatSession', JSON.stringify({ sessionId }));
    } else {
      localStorage.removeItem('chatSession');
    }
  }, [sessionId]);
  
  // Function to send a message
  const sendMessage = useCallback(async (content) => {
    if (!content.trim()) return;
    
    // Create a temporary message ID for optimistic UI update
    const tempMessageId = uuidv4();
    const userMessage = {
      id: tempMessageId,
      content,
      role: 'user',
      timestamp: new Date().toISOString(),
    };
    
    // Add user message to the chat
    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);
    setError(null);
    
    try {
      // Send the message to the server
      const { response, sessionId: newSessionId } = await chatService.sendChatMessage(content, sessionId);
      
      // Update session ID if this is a new session
      if (newSessionId && newSessionId !== sessionId) {
        setSessionId(newSessionId);
      }
      
      // Add AI response to the chat
      const aiMessage = {
        id: uuidv4(),
        content: response,
        role: 'assistant',
        timestamp: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
      // Save the updated chat history
      await chatService.saveChatSession(newSessionId || sessionId, [...messages, userMessage, aiMessage]);
      
      return aiMessage;
    } catch (err) {
      console.error('Error sending message:', err);
      setError(err.message || 'Failed to send message');
      
      // Remove the temporary message if there was an error
      setMessages(prev => prev.filter(msg => msg.id !== tempMessageId));
      
      // Re-throw the error for the component to handle if needed
      throw err;
    } finally {
      setIsTyping(false);
    }
  }, [sessionId, messages]);
  
  // Function to clear the chat
  const clearChat = useCallback(() => {
    setMessages([]);
    setSessionId(null);
    setError(null);
  }, []);
  
  // Function to send feedback for a message
  const sendFeedback = useCallback(async (messageId, rating, feedback = '') => {
    if (!sessionId || !messageId) return;
    
    try {
      await chatService.sendFeedback(sessionId, messageId, rating, feedback);
    } catch (err) {
      console.error('Error sending feedback:', err);
      // Fail silently for feedback errors
    }
  }, [sessionId]);
  
  // Function to load a saved chat session
  const loadSession = useCallback((session) => {
    setSessionId(session.id);
    setMessages(session.messages || []);
  }, []);
  
  // Value to be provided by the context
  const value = {
    messages,
    sessionId,
    isLoading,
    isTyping,
    error,
    sendMessage,
    clearChat,
    sendFeedback,
    loadSession,
  };
  
  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

export default ChatContext;
