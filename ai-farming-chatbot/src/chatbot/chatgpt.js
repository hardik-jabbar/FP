const { GoogleGenerativeAI } = require('@google/generative-ai');
require('dotenv').config();

// Use environment variable if set, otherwise fallback to hard-coded key provided by the user.
const API_KEY = process.env.GEMINI_API_KEY || 'AIzaSyAxVLfAhKPCsicBlTD37ISpOPW0Leyzaeg';
const genAI = new GoogleGenerativeAI(API_KEY);

// Keep the original exported name so existing imports continue to work
const getChatGPTResponse = async (userQuery) => {
    try {
        const model = genAI.getGenerativeModel({model: 'models/gemini-2.0-flash'});
        const result = await model.generateContent(userQuery);
        return result.response.text();
    } catch (error) {
        console.error('Error fetching response from Gemini:', error);
        throw new Error('Could not fetch response from the AI service.');
    }
};

module.exports = { getChatGPTResponse };