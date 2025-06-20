import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ChatProvider } from './contexts/ChatContext';
import ChatInterface from './components/ChatInterface';
import './App.css';

function App() {
  return (
    <Router>
      <ChatProvider>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            <Route path="/" element={<ChatInterface />} />
            <Route path="/chat" element={<ChatInterface />} />
            {/* Add more routes as needed */}
          </Routes>
        </div>
      </ChatProvider>
    </Router>
  );
}

export default App;
