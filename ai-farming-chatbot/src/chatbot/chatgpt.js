// chatgpt.js - Handles AI chat functionality using Google's Generative AI
const { GoogleGenerativeAI } = require('@google/generative-ai');

// Configuration
const API_KEY = 'AIzaSyAxVLfAhKPCsicBlTD37ISpOPW0Leyzaeg';
const genAI = new GoogleGenerativeAI(API_KEY);
const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });

// System prompt to guide the AI's responses
const SYSTEM_PROMPT = `You are a helpful AI farming assistant. Provide concise, accurate, and practical advice about agriculture, crop management, livestock, and sustainable farming practices. 

Guidelines:
- Keep responses clear and to the point
- Use simple language suitable for farmers of all experience levels
- Focus on practical, actionable advice
- When appropriate, include relevant measurements and units
- If you don't know the answer, say so rather than guessing
- For health or safety concerns, recommend consulting with a professional
- Be supportive and encouraging to new farmers`;

// Chat history storage
const chatSessions = new Map();

/**
 * Get a response from Google's Generative AI
 * @param {string} userId - Unique identifier for the user's chat session
 * @param {string} userQuery - The user's message
 * @returns {Promise<string>} - The AI's response
 */
const getChatGPTResponse = async (userId, userQuery) => {
  try {
    // Initialize chat session if it doesn't exist
    if (!chatSessions.has(userId)) {
      const chat = model.startChat({
        history: [
          {
            role: 'user',
            parts: [{ text: SYSTEM_PROMPT }],
          },
          {
            role: 'model',
            parts: [{ text: 'I am your farming assistant. How can I help you with your agricultural needs today?' }],
          },
        ],
        generationConfig: {
          maxOutputTokens: 1000,
          temperature: 0.7,
        },
      });
      chatSessions.set(userId, chat);
    }

    const chat = chatSessions.get(userId);
    const result = await chat.sendMessage(userQuery);
    const response = await result.response;
    const text = response.text();
    
    return text;

  } catch (error) {
    console.error('Error in getChatGPTResponse:', error);
    // Fallback responses
    const fallbackResponses = [
      "I'm having trouble connecting to the AI service. Please try again in a moment.",
      "I'm currently experiencing some technical difficulties. Could you try asking again?",
      "I apologize, but I'm unable to process your request right now. Please try again shortly."
    ];
    return fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)];
  }
};

module.exports = {
  getChatGPTResponse
};