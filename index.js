// This file is just a placeholder for Vercel to recognize the project as a Node.js project
// The actual server code is in FARMPOWER/server.js
console.log('Vercel serverless function initialized');

// This export is required for Vercel to recognize this as a serverless function
export default (req, res) => {
  res.status(200).json({ message: 'Welcome to FarmPower API' });
};
