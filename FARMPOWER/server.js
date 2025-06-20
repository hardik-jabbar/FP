const express = require('express');
const http = require('http');
const fs = require('fs');
const socketIo = require('socket.io');
const cors = require('cors');
const path = require('path');
const multer = require('multer');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
require('dotenv').config();

// Initialize Express app
const app = express();
const server = http.createServer(app);

// Socket.io setup (disable in production if not needed)
let io;
if (process.env.NODE_ENV !== 'production') {
  io = socketIo(server, {
    cors: {
      origin: '*',
      methods: ['GET', 'POST']
    }
  });

  io.on('connection', (socket) => {
    console.log('Client connected');
    socket.on('disconnect', () => {
      console.log('Client disconnected');
    });
  });
}

// Security middleware with CSP
app.use(helmet({
  contentSecurityPolicy: false, // Disable default CSP
  crossOriginEmbedderPolicy: false,
  crossOriginOpenerPolicy: false,
  crossOriginResourcePolicy: { policy: "cross-origin" },
  xssFilter: true,
  noSniff: true,
  hidePoweredBy: true,
  frameguard: { action: 'deny' }
}));

// Set CSP headers manually
app.use((req, res, next) => {
  // Remove all Permissions-Policy headers first
  res.removeHeader('Permissions-Policy');
  
  // Set CSP headers
  res.setHeader(
    'Content-Security-Policy',
    "default-src 'self'; " +
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://cdn.auth0.com https://vercel.live https://fp-omega.vercel.app; " +
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; " +
    "img-src 'self' data: https:; " +
    "font-src 'self' https://fonts.gstatic.com; " +
    "connect-src 'self' https://*.auth0.com https://*.vercel.app; " +
    "frame-src 'self' https://*.auth0.com; " +
    "object-src 'none'; " +  // Disable plugins
    "base-uri 'self'; " +    // Restrict base tag
    "form-action 'self';"    // Restrict form actions
  );
  
  // Set other security headers
  res.setHeader(
    'Referrer-Policy',
    'strict-origin-when-cross-origin'
  );
  
  next();
});

// Performance and logging
app.use(compression());
app.use(morgan('dev'));

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// CORS configuration
const allowedOrigins = [
  'http://localhost:3000',
  'http://localhost:3001',
  'https://*.vercel.app',
  'https://farmpower.vercel.app',  // Update this with your Vercel URL
  'https://www.farmpower.app'      // Your custom domain if you have one
];

const corsOptions = {
  origin: function (origin, callback) {
    // Allow requests with no origin (like mobile apps or curl requests)
    if (!origin) return callback(null, true);
    
    if (process.env.NODE_ENV === 'development' || 
        allowedOrigins.some(allowedOrigin => origin === allowedOrigin || origin.endsWith('.vercel.app'))) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,
  optionsSuccessStatus: 200
};
app.use(cors(corsOptions));

// Serve static files with proper caching
const staticOptions = {
  maxAge: '1y',
  etag: true,
  lastModified: true,
  setHeaders: (res, path) => {
    if (path.endsWith('.html')) {
      res.setHeader('Cache-Control', 'public, max-age=0, must-revalidate');
    }
  }
};

// Configure static file serving with proper MIME types and caching
const serveStatic = (path) => {
  return express.static(path, {
    setHeaders: (res, filePath) => {
      // Set proper content-type headers for different file types
      if (filePath.endsWith('.css')) {
        res.setHeader('Content-Type', 'text/css');
      } else if (filePath.endsWith('.js')) {
        res.setHeader('Content-Type', 'application/javascript');
      } else if (filePath.endsWith('.html')) {
        res.setHeader('Content-Type', 'text/html');
      } else if (filePath.endsWith('.json')) {
        res.setHeader('Content-Type', 'application/json');
      } else if (filePath.match(/\.(jpg|jpeg|png|gif|svg|ico)$/i)) {
        const ext = filePath.split('.').pop().toLowerCase();
        res.setHeader('Content-Type', `image/${ext === 'jpg' ? 'jpeg' : ext}`);
      }
      
      // Set caching headers
      res.setHeader('Cache-Control', 'public, max-age=31536000'); // 1 year cache
    }
  });
};

// Serve static files from the root directory
app.use(serveStatic(__dirname));

// Serve scripts from the scripts directory
app.use('/scripts', serveStatic(path.join(__dirname, 'scripts')));

// Serve assets from the assets directory
app.use('/assets', serveStatic(path.join(__dirname, 'assets')));

// Serve assets from the assets directory
app.use('/assets', express.static(path.join(__dirname, 'assets'), staticOptions));

// Add a middleware to ensure all asset paths are relative
app.use((req, res, next) => {
  if (req.path.endsWith('.css') || req.path.endsWith('.js') || req.path.endsWith('.png') || req.path.endsWith('.jpg') || req.path.endsWith('.jpeg') || req.path.endsWith('.svg') || req.path.endsWith('.gif')) {
    // Ensure the path is relative to the root
    const filePath = path.join(__dirname, req.path.startsWith('/') ? req.path.substr(1) : req.path);
    if (fs.existsSync(filePath)) {
      res.sendFile(filePath);
      return;
    }
  }
  next();
});

// Serve individual HTML files directly
app.get('*.html', (req, res, next) => {
  const filePath = path.join(__dirname, req.path);
  fs.access(filePath, fs.constants.F_OK, (err) => {
    if (!err) {
      res.sendFile(filePath);
    } else {
      next(); // Forward to the next middleware if file doesn't exist
    }
  });
});

// Serve index.html for all other routes (SPA routing)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err.stack);
  res.status(500).json({
    error: 'Something went wrong!',
    ...(process.env.NODE_ENV === 'development' && { details: err.message })
  });
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.status(200).json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API Routes
const apiRouter = express.Router();

// Configure multer for file uploads (in-memory for Vercel)
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 5 * 1024 * 1024, // 5MB limit
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only JPG, PNG, and GIF are allowed.'));
    }
  }
});

// Equipment routes
apiRouter.post('/equipment', upload.array('images', 5), (req, res) => {
  try {
    // Handle file uploads (in a real app, you'd upload to S3 or similar)
    const fileInfo = req.files.map(file => ({
      originalname: file.originalname,
      size: file.size,
      mimetype: file.mimetype,
      // In production, upload to cloud storage and return the URL
      url: `/api/uploads/${Date.now()}-${file.originalname}`
    }));

    const equipment = {
      ...req.body,
      images: fileInfo
    };
    
    // Emit update to all connected clients
    if (io) {
      io.emit('equipment-update', equipment);
    }
    
    res.status(201).json(equipment);
  } catch (error) {
    console.error('Error listing equipment:', error);
    res.status(500).json({ error: 'Failed to list equipment', details: error.message });
  }
});

// Newsletter subscription
apiRouter.post('/newsletter/subscribe', (req, res) => {
  try {
    const { email } = req.body;
    if (!email || !/\S+@\S+\.\S+/.test(email)) {
      return res.status(400).json({ error: 'Valid email is required' });
    }
    
    // In a real app, save to database or send to email service
    console.log(`New newsletter subscription: ${email}`);
    
    res.status(200).json({ 
      success: true, 
      message: 'Successfully subscribed to newsletter',
      email
    });
  } catch (error) {
    console.error('Error subscribing to newsletter:', error);
    res.status(500).json({ 
      error: 'Failed to subscribe to newsletter',
      details: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

// Mount API routes
app.use('/api', apiRouter);

// Serve SPA (Single Page Application)
app.get('*', (req, res) => {
  // If the request is for an API route, skip SPA serving
  if (req.path.startsWith('/api/')) {
    return res.status(404).json({ error: 'Not found' });
  }
  
  // For all other routes, serve index.html
  res.sendFile(path.join(__dirname, 'index.html'), (err) => {
    if (err) {
      console.error('Error sending file:', err);
      res.status(500).send('Error loading the application');
    }
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err.stack);
  res.status(500).json({
    error: 'Something went wrong!',
    ...(process.env.NODE_ENV === 'development' && { details: err.message })
  });
});

// Export the Express API for Vercel
module.exports = app;

// Only start the server if this file is run directly (not when imported as a module)
if (require.main === module) {
  const PORT = process.env.PORT || 3001;
  server.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running in ${process.env.NODE_ENV || 'development'} mode on port ${PORT}`);
    console.log(`Visit http://localhost:${PORT}`);
  });
} 