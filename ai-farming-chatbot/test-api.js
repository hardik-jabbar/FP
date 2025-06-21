import axios from 'axios';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const API_BASE_URL = 'http://localhost:5001/api';

// Helper function to make API requests
async function makeRequest(method, endpoint, data = null, headers = {}) {
  try {
    const config = {
      method,
      url: `${API_BASE_URL}${endpoint}`,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      data: data ? JSON.stringify(data) : undefined
    };

    console.log(`\nMaking ${method} request to ${endpoint}`);
    const response = await axios(config);
    
    console.log('Response:', {
      status: response.status,
      statusText: response.statusText,
      data: response.data
    });
    
    return response.data;
  } catch (error) {
    if (error.response) {
      console.error('Error response:', {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data
      });
    } else {
      console.error('Error:', error.message);
    }
    throw error;
  }
}

// Test the chat endpoint
async function testChat() {
  console.log('\n=== Testing Chat Endpoint ===');
  
  // First message (new session)
  console.log('\nSending first message...');
  const firstResponse = await makeRequest('POST', '/chat', {
    query: 'What are some best practices for organic farming?',
    sessionId: null
  });
  
  const sessionId = firstResponse.sessionId;
  console.log('\nSession ID:', sessionId);
  
  // Second message (continuing session)
  console.log('\nSending follow-up message...');
  await makeRequest('POST', '/chat', {
    query: 'Tell me more about crop rotation',
    sessionId
  });
}

// Test invalid request
async function testInvalidRequest() {
  console.log('\n=== Testing Invalid Request ===');
  try {
    await makeRequest('POST', '/chat', {
      query: '', // Empty query should be invalid
      sessionId: 'test-session-123'
    });
  } catch (error) {
    console.log('Expected error received for invalid request');
  }
}

// Run all tests
async function runTests() {
  try {
    await testChat();
    await testInvalidRequest();
    console.log('\n=== All tests completed ===');
  } catch (error) {
    console.error('\n=== Tests failed ===');
    process.exit(1);
  }
}

runTests();
