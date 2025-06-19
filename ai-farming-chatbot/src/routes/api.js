const express = require('express');
const router = express.Router();
const { getChatGPTResponse } = require('../chatbot/chatgpt');

// Endpoint to handle user queries
router.post('/chat', async (req, res) => {
    const userQuery = req.body.query;

    try {
        const response = await getChatGPTResponse(userQuery);
        res.json({ response });
    } catch (error) {
        console.error('Error fetching response from ChatGPT:', error);
        res.status(500).json({ error: 'An error occurred while processing your request.' });
    }
});

module.exports = router;