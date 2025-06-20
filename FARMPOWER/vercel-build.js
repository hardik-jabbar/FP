// This script ensures the public directory exists and contains necessary files
const fs = require('fs');
const path = require('path');

const publicDir = path.join(__dirname, 'public');

// Create public directory if it doesn't exist
if (!fs.existsSync(publicDir)) {
  fs.mkdirSync(publicDir, { recursive: true });
}

// Copy index.html to public directory if it doesn't exist
const indexSrc = path.join(__dirname, 'index.html');
const indexDest = path.join(publicDir, 'index.html');

if (fs.existsSync(indexSrc) && !fs.existsSync(indexDest)) {
  fs.copyFileSync(indexSrc, indexDest);
  console.log('Copied index.html to public directory');
}

console.log('Vercel build completed successfully');
