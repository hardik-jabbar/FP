# FarmPower Backend Deployment Documentation

## Project Overview
FarmPower is a FastAPI-based backend service with PostgreSQL database, containerized using Docker and deployed on Railway. The project uses Alembic for database migrations and includes a CI/CD pipeline with GitHub Actions.

## Tech Stack
- **Backend**: FastAPI (Python 3.13)
- **Database**: PostgreSQL (Supabase in production)
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Deployment**: Railway
- **Environment Management**: python-dotenv

## Project Structure
```
farmpower_backend_v2/
├── alembic/                  # Database migrations
│   ├── versions/            # Migration scripts
│   ├── env.py              # Alembic environment configuration
│   └── script.py.mako      # Migration template
├── models/                  # SQLAlchemy models
├── .github/
│   └── workflows/          # GitHub Actions workflows
│       └── deploy.yml      # Deployment workflow
├── .env.example            # Environment variables template
├── alembic.ini             # Alembic configuration
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker configuration
└── requirements.txt        # Python dependencies
```

## Local Development Setup

### Prerequisites
- Python 3.13
- Docker and Docker Compose
- Git

### Environment Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd farmpower_backend_v2
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file:
   ```bash
   cp .env.example .env
   ```
   Update the `.env` file with your local configuration.

### Database Setup
1. Start the database container:
   ```bash
   docker compose up db -d
   ```

2. Run database migrations:
   ```bash
   PYTHONPATH=$PYTHONPATH:. alembic upgrade head
   ```

### Running the Application
1. Start all services:
   ```bash
   docker compose up --build
   ```

2. Access the API at `http://localhost:8000`

## Production Deployment

### Railway Setup
1. Create a Railway account at https://railway.app
2. Create a new project
3. Add a PostgreSQL database
4. Get your Railway token and project ID

### Supabase Setup
1. Create a Supabase project
2. Get your database URL and API key
3. Update environment variables with Supabase credentials

### GitHub Secrets
Add the following secrets to your GitHub repository:
- `RAILWAY_TOKEN`: Your Railway authentication token
- `RAILWAY_PROJECT_ID`: Your Railway project ID
- `SUPABASE_DB_URL`: Your Supabase database URL
- `SUPABASE_KEY`: Your Supabase API key

### Deployment Process
1. Push to main branch triggers GitHub Actions workflow
2. Workflow:
   - Runs tests
   - Builds Docker image
   - Deploys to Railway
   - Runs database migrations

## Configuration Files

### Dockerfile
Multi-stage build for optimized production image:
```dockerfile
# Builder stage
FROM python:3.13-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.13-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    libpq5
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY . .
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
Local development configuration:
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DB_HOST=db
      - DB_PORT=5432
      - DB_NAME=farmpower
      - DB_USER=postgres
      - DB_PASSWORD=postgres
    depends_on:
      - db
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=farmpower
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### GitHub Actions Workflow
Automated deployment pipeline:
```yaml
name: Deploy to Railway
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: |
        pytest --cov=./ --cov-report=xml
    - name: Install Railway CLI
      run: |
        curl -fsSL https://railway.app/install.sh | sh
    - name: Deploy to Railway
      if: github.ref == 'refs/heads/main'
      run: |
        railway up
      env:
        RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        RAILWAY_PROJECT_ID: ${{ secrets.RAILWAY_PROJECT_ID }}
```

## Database Migrations

### Alembic Configuration
The project uses Alembic for database migrations with the following setup:

1. `alembic.ini`: Main configuration file
2. `alembic/env.py`: Environment-specific configuration
3. Migration scripts in `alembic/versions/`

### Running Migrations
```bash
# Create a new migration
PYTHONPATH=$PYTHONPATH:. alembic revision --autogenerate -m "Description"

# Apply migrations
PYTHONPATH=$PYTHONPATH:. alembic upgrade head

# Rollback migrations
PYTHONPATH=$PYTHONPATH:. alembic downgrade -1
```

## Security Considerations

### Rate Limiting
The application implements rate limiting using `slowapi` with the following configuration:

- **Default Rate Limit**: 100 requests per minute
- **Authentication Endpoints**: 5 requests per minute
- **API Endpoints**: 1000 requests per hour

Rate limits can be configured through environment variables:
```bash
RATE_LIMIT=100/minute
RATE_LIMIT_AUTH=5/minute
RATE_LIMIT_API=1000/hour
```

When rate limits are exceeded, the API returns a 429 status code with:
```json
{
    "error": "Rate limit exceeded",
    "detail": "Too many requests. Please try again in X seconds.",
    "retry_after": X
}
```

### Environment Variables
- All sensitive data is stored in environment variables
- `.env` file is git-ignored
- Production secrets are stored in Railway and GitHub Secrets

### CORS Configuration
- Configured to only allow requests from the frontend domain
- Production CORS settings are environment-specific

### Database Security
- Production database is hosted on Supabase
- Connection strings are encrypted
- Database credentials are never committed to version control

## Monitoring and Maintenance

### Logging
- Application logs are available in Railway dashboard
- GitHub Actions workflow logs for deployment status

### Database Maintenance
- Regular backups through Supabase
- Migration history tracked in Alembic versions

## Troubleshooting

### Common Issues
1. Database Connection:
   - Verify environment variables
   - Check database container status
   - Ensure correct database credentials

2. Migration Issues:
   - Check Alembic version history
   - Verify model changes
   - Ensure database is accessible

3. Deployment Issues:
   - Check GitHub Actions logs
   - Verify Railway configuration
   - Ensure all secrets are properly set

## Support and Contact
For technical support or questions, please contact the development team.

## License
[Your License Information] 