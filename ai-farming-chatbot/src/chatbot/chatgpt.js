// chatgpt.js - Handles AI chat functionality using Google's Generative AI
import 'dotenv/config';
import { GoogleGenerativeAI } from '@google/generative-ai';
import winston from 'winston';

// Logger configuration
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  defaultMeta: { service: 'ai-chatbot' },
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ 
      filename: 'logs/ai-error.log', 
      level: 'error' 
    }),
    new winston.transports.File({ 
      filename: 'logs/ai-combined.log' 
    })
  ]
});

// Configuration
const API_KEY = process.env.GOOGLE_AI_API_KEY;
if (!API_KEY) {
  const errorMsg = 'GOOGLE_AI_API_KEY is not set in environment variables';
  logger.error(errorMsg);
  throw new Error('AI service is not properly configured');
}

const genAI = new GoogleGenerativeAI(API_KEY);
const model = genAI.getGenerativeModel({ 
  model: 'gemini-1.5-flash',
  generationConfig: {
    maxOutputTokens: 1000,
    temperature: 0.7,
    topP: 0.9,
    topK: 40,
  },
  safetySettings: [
    {
      category: 'HARM_CATEGORY_HARASSMENT',
      threshold: 'BLOCK_MEDIUM_AND_ABOVE',
    },
    {
      category: 'HARM_CATEGORY_HATE_SPEECH',
      threshold: 'BLOCK_MEDIUM_AND_ABOVE',
    },
    {
      category: 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
      threshold: 'BLOCK_MEDIUM_AND_ABOVE',
    },
    {
      category: 'HARM_CATEGORY_DANGEROUS_CONTENT',
      threshold: 'BLOCK_MEDIUM_AND_ABOVE',
    },
  ],
});

// System prompt to guide the AI's responses
const SYSTEM_PROMPT = `You are a helpful AI farming assistant. Provide concise, accurate, and practical advice about agriculture, crop management, livestock, and sustainable farming practices. 

Guidelines:
- Keep responses clear and to the point
- Use simple language suitable for farmers of all experience levels
- Focus on practical, actionable advice
- When appropriate, include relevant measurements and units
- If you don't know the answer, say so rather than guessing
- For health or safety concerns, recommend consulting with a professional
- Be supportive and encouraging to new farmers
- Always respond in the same language as the user's query`;

// Chat history storage with TTL (Time To Live)
const chatSessions = new Map();
const SESSION_TTL = 1000 * 60 * 60 * 24; // 24 hours

// Clean up old sessions periodically
setInterval(() => {
  const now = Date.now();
  for (const [userId, session] of chatSessions.entries()) {
    if (now - session.lastActive > SESSION_TTL) {
      chatSessions.delete(userId);
      logger.info(`Cleaned up expired session: ${userId}`);
    }
  }
}, 1000 * 60 * 30); // Run every 30 minutes

/**
 * Get a response from Google's Generative AI
 * @param {string} userId - Unique identifier for the user's chat session
 * @param {string} userQuery - The user's message
 * @returns {Promise<{response: string, sessionId: string}>} - The AI's response and session ID
 */
export const getChatGPTResponse = async (userId, userQuery) => {
  const startTime = Date.now();
  const requestId = `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  
  try {
    logger.info({
      message: 'Processing AI request',
      requestId,
      userId,
      queryLength: userQuery.length,
      timestamp: new Date().toISOString()
    });

    // Validate input
    if (!userQuery || typeof userQuery !== 'string' || userQuery.trim().length === 0) {
      throw new Error('Invalid query: Query must be a non-empty string');
    }

    // Initialize or update chat session
    if (!chatSessions.has(userId)) {
      const chat = model.startChat({
        history: [
          {
            role: 'user',
            parts: [{ text: SYSTEM_PROMPT }],
          },
          {
            role: 'model',
            parts: [{ 
              text: 'I am your farming assistant. How can I help you with your agricultural needs today?' 
            }],
          },
        ],
      });
      
      chatSessions.set(userId, {
        chat,
        lastActive: Date.now(),
        createdAt: new Date().toISOString(),
        messageCount: 0
      });
      
      logger.info({
        message: 'Created new chat session',
        requestId,
        userId,
        timestamp: new Date().toISOString()
      });
    }

    const session = chatSessions.get(userId);
    session.lastActive = Date.now();
    session.messageCount += 1;

    // Send message to AI
    const result = await session.chat.sendMessage(userQuery);
    const response = await result.response;
    const responseText = response.text();

    // Log successful response
    logger.info({
      message: 'AI response generated',
      requestId,
      userId,
      responseLength: responseText.length,
      processingTimeMs: Date.now() - startTime,
      timestamp: new Date().toISOString()
    });

    return {
      response: responseText,
      sessionId: userId
    };
  } catch (error) {
    const errorDetails = {
      message: 'Error in getChatGPTResponse',
      requestId,
      userId,
      error: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined,
      processingTimeMs: Date.now() - startTime,
      timestamp: new Date().toISOString()
    };
    
    logger.error(errorDetails);
    
    // Rethrow with user-friendly message
    throw new Error(
      error.message.includes('API key not valid')
        ? 'Authentication error with AI service. Please contact support.'
        : 'Sorry, I encountered an error processing your request. Please try again later.'
    );
  }
};