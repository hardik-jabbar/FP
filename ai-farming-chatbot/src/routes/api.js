import express from 'express';
import { getChatGPTResponse } from '../chatbot/chatgpt.js';
import { v4 as uuidv4 } from 'uuid';
import winston from 'winston';

const router = express.Router();

// Logger configuration
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  defaultMeta: { service: 'api-routes' },
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ 
      filename: 'logs/api-error.log',
      level: 'error' 
    }),
    new winston.transports.File({ 
      filename: 'logs/api-combined.log' 
    })
  ]
});

// Rate limiting middleware (applied at the router level)
const rateLimit = require('express-rate-limit');

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res) => {
    logger.warn({
      message: 'Rate limit exceeded',
      ip: req.ip,
      path: req.path,
      method: req.method
    });
    
    res.status(429).json({
      error: 'Too many requests, please try again later.'
    });
  }
});

// Apply rate limiting to all API routes
router.use(apiLimiter);

/**
 * @route POST /api/chat
 * @desc Get a response from the AI
 * @access Public
 */
router.post('/chat', async (req, res, next) => {
  const startTime = Date.now();
  const requestId = uuidv4();
  const { query, sessionId: clientSessionId } = req.body;
  
  // Log the incoming request
  logger.info({
    message: 'Incoming chat request',
    requestId,
    sessionId: clientSessionId || 'none',
    queryLength: query ? query.length : 0,
    timestamp: new Date().toISOString()
  });
  
  // Validate request
  if (!query || typeof query !== 'string' || query.trim().length === 0) {
    const error = new Error('Query is required and must be a non-empty string');
    error.statusCode = 400;
    return next(error);
  }
  
  // Truncate very long queries to prevent abuse
  const truncatedQuery = query.length > 1000 ? query.substring(0, 1000) + '...' : query;
  
  try {
    // Use existing session ID or generate a new one
    const sessionId = clientSessionId || `sess-${uuidv4()}`;
    
    // Get AI response
    const { response } = await getChatGPTResponse(sessionId, truncatedQuery);
    
    // Log successful response
    logger.info({
      message: 'Chat response sent',
      requestId,
      sessionId,
      responseLength: response.length,
      processingTimeMs: Date.now() - startTime,
      timestamp: new Date().toISOString()
    });
    
    // Send response
    res.json({ 
      success: true,
      response,
      sessionId,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    // Log the error
    logger.error({
      message: 'Error in chat endpoint',
      requestId,
      sessionId: clientSessionId || 'none',
      error: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined,
      processingTimeMs: Date.now() - startTime,
      timestamp: new Date().toISOString()
    });
    
    // Handle different types of errors
    if (error.message.includes('API key not valid')) {
      error.statusCode = 500;
      error.message = 'Authentication error with AI service';
    } else if (error.message.includes('rate limit')) {
      error.statusCode = 429;
      error.message = 'Rate limit exceeded for AI service';
    } else if (!error.statusCode) {
      error.statusCode = 500;
      error.message = 'Failed to get response from AI';
    }
    
    next(error);
  }
});

// Health check endpoint
router.get('/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'AI Chat API',
    version: process.env.npm_package_version || '1.0.0'
  });
});

// 404 handler for API routes
router.use((req, res) => {
  res.status(404).json({
    success: false,
    error: 'API endpoint not found',
    timestamp: new Date().toISOString()
  });
});

// Error handling middleware
router.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  const response = {
    success: false,
    error: err.message || 'Internal Server Error',
    timestamp: new Date().toISOString()
  };
  
  // Include stack trace in development
  if (process.env.NODE_ENV === 'development') {
    response.stack = err.stack;
  }
  
  res.status(statusCode).json(response);
});

export default router;