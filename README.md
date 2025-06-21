# FarmPower Digital Platform

An integrated digital platform empowering farmers and agricultural stakeholders with modern tools and technologies.

## Project Overview

FarmPower is a comprehensive digital solution designed to enhance farming operations through:
- Streamlined farm oversight and real-time asset tracking
- Data-driven insights for better decision-making
- Robust marketplaces for agricultural equipment and parts
- Seamless communication between users and service providers
- AI-powered assistance for farming-related queries using Google's Generative AI

## 🚀 Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- Git (for cloning the repository)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd farmpower
   ```

2. **Start the services**
   ```bash
   docker-compose up -d
   ```

3. **Access the services**
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - PostgreSQL: localhost:5432

4. **View logs**
   ```bash
   docker-compose logs -f
   ```

### Frontend Development

For frontend development, we recommend running the frontend separately:

```bash
cd FARMPOWER
npm install
npm run dev
```

## Project Structure

```
farmpower/
├── farmpower_backend_v2/    # Backend API (FastAPI)
│   ├── app/                # Application code
│   ├── models/             # Database models
│   └── requirements.txt    # Python dependencies
│
├── FARMPOWER/             # Frontend application (Vue.js/React)
│   ├── assets/            # Static assets (images, icons)
│   ├── components/        # Reusable UI components
│   ├── scripts/             # JavaScript files
│   └── templates/           # HTML templates
├── backend/                 # Backend application
│   ├── app/                # Main application code
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core functionality
│   │   ├── models/        # Database models
│   │   └── schemas/       # Pydantic schemas
│   ├── tests/             # Test files
│   └── requirements.txt    # Python dependencies
├── ai-chatbot/            # AI Farming Chatbot service
└── docker/               # Docker configuration files
```

## Key Features

### Phase 1 (MVP)

1. **User Management**
   - User registration and authentication
   - Profile management
   - Email verification

2. **Equipment Marketplace**
   - Tractor listings
   - Search and filtering
   - Image upload support

3. **GPS Tracking & Field Planning**
   - Interactive map interface
   - Field boundary management
   - Equipment location tracking

4. **Crop Calculator**
   - Profitability analysis
   - Cost calculations
   - Yield projections

5. **Basic Communication**
   - Simple messaging system
   - Basic notification system
   - AI chatbot integration

## Technical Stack

### Frontend
- HTML5, Tailwind CSS
- JavaScript
- Mapbox for mapping
- Responsive design

### Backend
- Python 3.x
- FastAPI
- SQLAlchemy
- PostgreSQL
- AWS S3 for storage

### AI Chatbot
- Node.js
- Express.js
- ChatGPT API integration

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/farmpower.git
   cd farmpower
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   - Copy `.env-example` to `.env`
   - Update environment variables

4. **Database Setup**
   ```bash
   python create_tables.py
   ```

5. **Run the Backend**
   ```bash
   uvicorn main:app --reload
   ```

6. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

## Development Guidelines

1. **Code Style**
   - Follow PEP 8 for Python code
   - Use ESLint for JavaScript
   - Write meaningful commit messages

2. **Testing**
   - Write unit tests for new features
   - Run tests before committing
   - Maintain test coverage

3. **Documentation**
   - Document API endpoints
   - Update README for major changes
   - Comment complex code sections

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For support or queries, please contact [your-email@example.com] 