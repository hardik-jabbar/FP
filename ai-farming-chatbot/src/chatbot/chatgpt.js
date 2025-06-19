// Mock response system for testing
const mockResponses = {
  'hello': 'Hello! I\'m your FarmPower AI assistant. How can I help with your farming questions today?',
  'hi': 'Hi there! I\'m here to help with all your agricultural needs. What would you like to know?',
  'help': 'I can help with crop advice, soil health, pest control, and general farming questions. What do you need help with?',
  'soil': 'Healthy soil is key to successful farming. Consider testing your soil pH, adding organic matter, and practicing crop rotation.',
  'pests': 'Common pests can be managed with integrated pest management (IPM) techniques. What specific pest are you dealing with?',
  'weather': 'Weather greatly impacts farming. Always check local forecasts and consider using weather-resistant crop varieties.',
  'fertilizer': 'The right fertilizer depends on your soil type and crops. A soil test can help determine what nutrients your soil needs.',
  'organic': 'Organic farming focuses on natural methods. Consider composting, natural pest control, and crop diversity.',
  'default': 'I\'m your FarmPower AI assistant, here to help with all your agricultural questions. How can I assist you today?'
};

const getChatGPTResponse = async (userQuery) => {
  try {
    console.log('Processing query:', userQuery);
    
    // Simple keyword matching for demo purposes
    const query = userQuery.toLowerCase().trim();
    let response = mockResponses.default;
    
    // Check for matching keywords
    for (const [keyword, reply] of Object.entries(mockResponses)) {
      if (query.includes(keyword)) {
        response = reply;
        break;
      }
    }
    
    // Add a small delay to simulate API call
    await new Promise(resolve => setTimeout(resolve, 500));
    
    console.log('Sending response:', response);
    return response;
    
  } catch (error) {
    console.error('Error in getChatGPTResponse:', error);
    return "I'm having some trouble processing your request. Please try again with a different question.";
  }
};

module.exports = { getChatGPTResponse };