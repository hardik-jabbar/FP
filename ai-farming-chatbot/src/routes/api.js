const express = require('express');
const router = express.Router();
const { getChatGPTResponse } = require('../chatbot/chatgpt');

// In-memory storage for user sessions (in production, use a proper session store)
const userSessions = new Map();

/**
 * Generate a unique session ID for each user
 * @returns {string} A unique session ID
 */
const generateSessionId = () => {
    return 'user-' + Math.random().toString(36).substr(2, 9);
};

/**
 * @route POST /api/chat
 * @desc Get a response from the AI
 * @access Public
 */
router.post('/chat', async (req, res) => {
    const { query, sessionId: clientSessionId } = req.body;
    
    if (!query) {
        return res.status(400).json({ error: 'Query is required' });
    }
    
    try {
        // Use existing session ID or create a new one
        let sessionId = clientSessionId;
        if (!sessionId || !userSessions.has(sessionId)) {
            sessionId = generateSessionId();
            userSessions.set(sessionId, { createdAt: Date.now() });
        }
        
        const response = await getChatGPTResponse(sessionId, query);
        res.json({ 
            response,
            sessionId // Send back the session ID to maintain conversation context
        });
    } catch (error) {
        console.error('Error in chat endpoint:', error);
        res.status(500).json({ 
            error: 'Failed to get response from AI',
            details: process.env.NODE_ENV === 'development' ? error.message : undefined
        });
    }
});

// Clean up old sessions periodically (every hour)
setInterval(() => {
    const now = Date.now();
    const maxSessionAge = 24 * 60 * 60 * 1000; // 24 hours
    
    for (const [sessionId, data] of userSessions.entries()) {
        if (now - data.createdAt > maxSessionAge) {
            userSessions.delete(sessionId);
        }
    }
}, 60 * 60 * 1000); // Run every hour

module.exports = router;