# Car Fault Diagnosis Backend

This is the FastAPI backend for the Car Fault Diagnosis mobile application.

## Features

- JWT Authentication
- User and Mechanic management
- Diagnostic file upload and processing
- Feedback system
- PostgreSQL database with SQLAlchemy ORM
- Alembic database migrations

## Setup

1. **Install dependencies:**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

2. **Set up environment variables:**
   \`\`\`bash
   cp .env.example .env
   # Edit .env with your database URL and other settings
   \`\`\`

3. **Initialize database:**
   \`\`\`bash
   alembic upgrade head
   \`\`\`

4. **Run the server:**
   \`\`\`bash
   uvicorn main:app --reload
   \`\`\`

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Migrations

Create a new migration:
\`\`\`bash
alembic revision --autogenerate -m "Description of changes"
\`\`\`

Apply migrations:
\`\`\`bash
alembic upgrade head
\`\`\`

## Docker Setup

Run with Docker Compose:
\`\`\`bash
docker-compose up -d
\`\`\`

This will start both the PostgreSQL database and the FastAPI application.

## Project Structure

\`\`\`
backend/
├── alembic/                 # Database migrations
├── routers/                 # API route handlers
│   ├── auth.py             # Authentication endpoints
│   ├── users.py            # User management
│   ├── mechanics.py        # Mechanic management
│   ├── diagnostics.py      # Diagnostic endpoints
│   └── feedback.py         # Feedback system
├── main.py                 # FastAPI application
├── models.py               # SQLAlchemy models
├── schemas.py              # Pydantic schemas
├── database.py             # Database configuration
├── auth.py                 # Authentication utilities
├── config.py               # Application settings
└── requirements.txt        # Python dependencies
\`\`\`

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `UPLOAD_DIR`: Directory for file uploads
- `AI_MODEL_URL`: URL for AI model service
- `YOUTUBE_API_KEY`: YouTube API key (optional)
