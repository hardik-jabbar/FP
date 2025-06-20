const { Handler } = require('@netlify/functions');

exports.handler = async (event, context) => {
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message: 'Hello from Netlify Function!' }),
  };
};
