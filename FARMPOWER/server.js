const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const path = require('path');
const multer = require('multer');
require('dotenv').config();

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname)));

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, path.join(__dirname, 'assets/uploads'))
  },
  filename: function (req, file, cb) {
    cb(null, Date.now() + '-' + file.originalname)
  }
});

const upload = multer({ storage: storage });

// Socket.io connection handling
io.on('connection', (socket) => {
  console.log('Client connected');

  socket.on('disconnect', () => {
    console.log('Client disconnected');
  });
});

// API Routes
app.post('/api/equipment', upload.array('images'), (req, res) => {
  try {
    // Handle equipment listing
    const equipment = {
      ...req.body,
      images: req.files.map(file => `/assets/uploads/${file.filename}`)
    };
    
    // Emit update to all connected clients
    io.emit('equipment-update', equipment);
    
    res.status(201).json(equipment);
  } catch (error) {
    console.error('Error listing equipment:', error);
    res.status(500).json({ error: 'Failed to list equipment' });
  }
});

app.post('/api/newsletter/subscribe', (req, res) => {
  try {
    const { email } = req.body;
    // Add newsletter subscription logic here
    res.status(200).json({ message: 'Successfully subscribed to newsletter' });
  } catch (error) {
    console.error('Error subscribing to newsletter:', error);
    res.status(500).json({ error: 'Failed to subscribe to newsletter' });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// Start server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
}); 