/**
 * Chat Service
 * 
 * Provides methods for interacting with the chat API.
 * Handles session management, message sending, and response processing.
 */

import { post, ApiError } from '../utils/api';
import config from '../config';

/**
 * Sends a chat message to the server and returns the AI's response
 * @param {string} message - The user's message
 * @param {string} [sessionId] - Optional session ID for continuing conversations
 * @returns {Promise<{response: string, sessionId: string}>} - The AI's response and session ID
 */
export async function sendChatMessage(message, sessionId = null) {
  try {
    const data = await post('/chat', {
      query: message,
      sessionId,
    });
    
    return {
      response: data.response,
      sessionId: data.sessionId,
    };
  } catch (error) {
    console.error('Error sending chat message:', error);
    
    // Handle specific error cases
    if (error.isApiError) {
      if (error.status === 401) {
        throw new Error('Authentication required. Please log in again.');
      } else if (error.status === 429) {
        throw new Error('Rate limit exceeded. Please wait before sending more messages.');
      } else if (error.status >= 500) {
        throw new Error('The chat service is currently unavailable. Please try again later.');
      }
    }
    
    // Re-throw with a user-friendly message if not handled above
    throw new Error('Failed to send message. Please check your connection and try again.');
  }
}

/**
 * Checks if the chat service is available
 * @returns {Promise<boolean>} - Whether the service is available
 */
export async function checkChatService() {
  try {
    const response = await fetch(`${config.api.baseUrl}/health`);
    const data = await response.json();
    return data.status === 'ok';
  } catch (error) {
    console.error('Error checking chat service:', error);
    return false;
  }
}

/**
 * Gets chat history for a specific session
 * @param {string} sessionId - The session ID
 * @returns {Promise<Array>} - The chat history
 */
export async function getChatHistory(sessionId) {
  try {
    const response = await fetch(`${config.api.baseUrl}/chat/history?sessionId=${encodeURIComponent(sessionId)}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching chat history:', error);
    throw new Error('Failed to load chat history');
  }
}

/**
 * Sends feedback for a chat response
 * @param {string} sessionId - The session ID
 * @param {string} messageId - The ID of the message being rated
 * @param {number} rating - The rating (1-5)
 * @param {string} [feedback] - Optional feedback text
 * @returns {Promise<void>}
 */
export async function sendFeedback(sessionId, messageId, rating, feedback = '') {
  try {
    await post('/feedback', {
      sessionId,
      messageId,
      rating,
      feedback,
    });
  } catch (error) {
    console.error('Error sending feedback:', error);
    // Fail silently for feedback errors
  }
}

/**
 * Saves the current chat session
 * @param {string} sessionId - The session ID
 * @param {Array} messages - The chat messages to save
 * @returns {Promise<void>}
 */
export async function saveChatSession(sessionId, messages) {
  try {
    await post('/chat/save', {
      sessionId,
      messages,
    });
  } catch (error) {
    console.error('Error saving chat session:', error);
    throw new Error('Failed to save chat session');
  }
}

/**
 * Gets a list of saved chat sessions
 * @returns {Promise<Array>} - List of saved sessions
 */
export async function getSavedSessions() {
  try {
    const response = await fetch(`${config.api.baseUrl}/chat/sessions`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching saved sessions:', error);
    throw new Error('Failed to load saved sessions');
  }
}

/**
 * Deletes a saved chat session
 * @param {string} sessionId - The session ID to delete
 * @returns {Promise<void>}
 */
export async function deleteChatSession(sessionId) {
  try {
    const response = await fetch(`${config.api.baseUrl}/chat/sessions/${encodeURIComponent(sessionId)}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  } catch (error) {
    console.error('Error deleting chat session:', error);
    throw new Error('Failed to delete chat session');
  }
}

export default {
  sendChatMessage,
  checkChatService,
  getChatHistory,
  sendFeedback,
  saveChatSession,
  getSavedSessions,
  deleteChatSession,
};
