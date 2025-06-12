# FarmPower

FarmPower is a comprehensive smart farming platform that helps farmers manage their equipment, track GPS locations, schedule services, and optimize crop profitability.

## Features

- Equipment Marketplace
- GPS Tracking
- Service Scheduling
- Parts Marketplace
- Crop Calculator
- Real-time Notifications
- User Management
- Responsive Design

## Tech Stack

- Frontend:
  - HTML5
  - Tailwind CSS
  - JavaScript
  - Socket.io Client
  - Auth0 SPA SDK

- Backend:
  - Node.js
  - Express
  - Socket.io
  - Multer (File Uploads)

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/farmpower.git
   cd farmpower
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file in the root directory with the following variables:
   ```
   PORT=3000
   NODE_ENV=development

   # Auth0 Configuration
   AUTH0_DOMAIN=your-auth0-domain.auth0.com
   AUTH0_CLIENT_ID=your-auth0-client-id
   AUTH0_CLIENT_SECRET=your-auth0-client-secret

   # API Configuration
   API_URL=http://localhost:3000
   SOCKET_URL=http://localhost:3000

   # File Upload Configuration
   MAX_FILE_SIZE=5242880 # 5MB in bytes
   ALLOWED_FILE_TYPES=image/jpeg,image/png,image/webp
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

5. Open your browser and navigate to `http://localhost:3000`

## Project Structure

```
FARMPOWER/
├── assets/           # Static assets (images, fonts, etc.)
├── components/       # Reusable HTML components
├── scripts/         # JavaScript utilities
├── styles/          # CSS styles
├── server.js        # Express server
├── package.json     # Project dependencies
└── README.md        # Project documentation
```

## Available Scripts

- `npm start` - Start the production server
- `npm run dev` - Start the development server with hot reload
- `npm run check-links` - Check for broken links and create missing pages
- `npm test` - Run tests

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 