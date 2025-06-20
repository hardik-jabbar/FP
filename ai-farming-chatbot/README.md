# 🌱 AI Farming Chatbot

## Overview
The AI Farming Chatbot is a modern web application that leverages Google's Generative AI to provide farmers and agricultural enthusiasts with valuable information and assistance. The application offers a user-friendly interface for interacting with an AI assistant that can answer questions and provide insights on various farming-related topics.

## 🚀 Features

- **Interactive Chat Interface**: Modern, responsive UI with real-time messaging
- **Session Management**: Persists conversations across page refreshes
- **Markdown Support**: Rich text formatting in messages
- **Responsive Design**: Works on desktop and mobile devices
- **Rate Limiting**: Protects the API from abuse
- **Error Handling**: Graceful error states and user feedback
- **Environment Configuration**: Easy configuration for different environments
- **Analytics Ready**: Built-in support for Google Analytics and error tracking

## 🏗️ Project Structure

```
ai-farming-chatbot/
├── public/               # Static files
│   ├── index.html        # Main HTML template
│   └── assets/           # Images, fonts, etc.
├── src/
│   ├── components/       # React components
│   ├── contexts/         # React contexts
│   ├── services/         # API and service layer
│   ├── utils/            # Utility functions
│   ├── config.js         # Application configuration
│   ├── App.jsx           # Main React component
│   └── index.js          # Application entry point
├── server/               # Backend server code
│   ├── routes/           # API routes
│   ├── middleware/       # Express middleware
│   └── server.js         # Server entry point
├── .env                  # Environment variables
├── .gitignore           # Git ignore file
├── package.json         # Project configuration
├── vite.config.js       # Vite configuration
├── tailwind.config.js   # Tailwind CSS configuration
└── postcss.config.js    # PostCSS configuration
```

## 🛠️ Setup Instructions

### Prerequisites

- Node.js 18.0.0 or higher
- npm 9.0.0 or higher
- Google AI API key (for the backend)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-farming-chatbot
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Update the values in `.env` with your configuration

4. **Start the development servers**
   ```bash
   # Start the backend server
   npm run dev
   
   # In a new terminal, start the frontend development server
   npm run dev:client
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

### Building for Production

```bash
# Build the frontend for production
npm run build

# Start the production server
npm start
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NODE_ENV` | Node environment | `development` |
| `PORT` | Backend server port | `5000` |
| `GOOGLE_AI_API_KEY` | Google AI API key | - |
| `VITE_API_BASE_URL` | Frontend API base URL | `http://localhost:5000/api` |

## 🤝 Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Google AI](https://ai.google/)
- [React](https://reactjs.org/)
- [Vite](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)

## Usage
- Type your questions related to farming, tractors, parts, agriculture, crops, GPS, land mapping, or improving crop yield in the chatbot interface.
- The chatbot will respond with relevant information and insights powered by the ChatGPT API.

## Capabilities
- Provides information on various farming topics.
- Assists with queries about tractors and agricultural equipment.
- Offers insights on crop management and yield improvement strategies.
- Supports GPS and land mapping inquiries.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.