# Book Management API

A production-ready FastAPI REST API for managing books with PostgreSQL, SQLAlchemy Async, Alembic, Pydantic v2, JWT authentication, RBAC, rate limiting, Redis caching, and more.

## Features

- **CRUD Operations** for books
- **JWT Authentication** (access & refresh tokens)
- **Role-Based Access Control (RBAC)**
- **Rate Limiting** using Redis
- **Request ID Middleware** for tracing
- **Structured Logging**
- **Environment-based Configuration** using pydantic-settings
- **Database Migrations** with Alembic
- **API Documentation** with Swagger UI and ReDoc
- **Dockerized** with docker-compose
- **Comprehensive Test Suite** with pytest
- **Code Quality** with Black, Ruff, and isort
- **AI Librarian Assistant** (Optional) - Natural language book search, recommendations, and metadata enrichment using LangGraph and LangChain

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy (Async)
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Authentication**: JWT (python-jose, passlib)
- **Caching**: Redis
- **Rate Limiting**: slowapi
- **Environment**: pydantic-settings, python-dotenv
- **Testing**: pytest, pytest-asyncio, httpx
- **Code Quality**: Black, Ruff, isort
- **Logging**: Loguru
- **Containerization**: Docker, docker-compose
- **AI/ML**: LangGraph, LangChain, OpenAI GPT (optional)

## AI Librarian Assistant

This project includes an optional AI Librarian Assistant built with LangGraph and LangChain:

- **Natural Language Book Search**: Users can search for books using conversational queries like "Show me science books by John"
- **Book Recommendations**: Get personalized recommendations based on books you like
- **Metadata Enrichment**: Get additional information about books including genre, summary, and suggested tags
- **Admin/Librarian Assistants**: Help librarians with book information and recommendations

### How It Works

1. **LangGraph** orchestrates the AI workflow using nodes for intent classification, routing, and response formatting
2. **LangChain** handles LLM integration, prompt templates, tools, and structured output parsing
3. The AI module connects to your existing book database/repository layer to provide accurate, real-time information
4. The assistant is optional and can be enabled/disabled via environment variables

### Architecture

```
Client
  ↓
FastAPI API Layer
  ├── Book CRUD APIs
  ├── Auth APIs
  ├── Health Check
  └── AI Assistant APIs (/api/v1/ai/assistant)
          ↓
      LangGraph AI Workflow
          ↓
      LangChain Components
          ├── LLM
          ├── Prompt Templates
          ├── Tools (search, recommend, enrich)
          ├── Output Parsers
          └── Retriever / DB Tool
          ↓
      PostgreSQL / Redis
```

### Configuration

Add these to your `.env` file to enable AI features:

```bash
# AI Assistant Settings (Optional Feature)
ENABLE_AI_ASSISTANT=true
LLM_PROVIDER=openai
LLM_API_KEY=your-openai-api-key-here
AI_MODEL=gpt-4o-mini
```

### Usage

When enabled, the AI assistant is available at:
```
POST /api/v1/ai/assistant
```

Request body:
```json
{
  "query": "Find available science books by John"
}
```

Response:
```json
{
  "answer": "I found 3 available science books by John.",
  "intent": "book_search",
  "books": [
    {
      "id": 1,
      "title": "Science Basics",
      "author": "John Smith",
      "genre": "Science",
      "available": true
    }
  ]
}
```

### Testing

The AI functionality is designed to be optional:
- Core CRUD APIs work independently of the AI module
- When `ENABLE_AI_ASSISTANT=false`, the AI endpoint returns a 503 Service Unavailable error
- For testing, you can mock the LangGraph responses to avoid calling external LLMs

## Getting Started

### Prerequisites

- Docker and docker-compose
- (Optional) Python 3.11+ for local development

### Running with Docker

1. Clone the repository
2. Copy `.env.example` to `.env` and adjust the environment variables as needed.
3. Run `docker-compose up --build`
4. The API will be available at `http://localhost:8000`
5. API documentation:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Local Development

1. Create a virtual environment: `python -m venv venv`
2. Activate it:
   - Linux/Mac: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Set up environment variables (copy `.env.example` to `.env`)
5. Apply database migrations: `alembic upgrade head`
6. Run the application: `uvicorn app.main:app --reload`
7. Run tests: `pytest`

## Project Structure

```
book_api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── routes/
│   │       │   ├── books.py
│   │       │   ├── auth.py
│   │       │   ├── health.py
│   │       │   └── ai.py
│   │       └── router.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── database/
│   │   ├── session.py
│   │   └── base.py
│   ├── models/
│   │   ├── book.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── book.py
│   │   ├── user.py
│   │   └── common.py
│   ├── repositories/
│   │   ├── book_repository.py
│   │   └── user_repository.py
│   ├── services/
│   │   ├── book_service.py
│   │   └── auth_service.py
│   ├── middleware/
│   │   ├── request_id.py
│   │   ├── logging.py
│   │   └── rate_limit.py
│   ├── exceptions/
│   │   ├── handlers.py
│   │   └── custom_exceptions.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── pagination.py
│   ├── ai/
│   │   ├── graph.py
│   │   ├── nodes.py
│   │   ├── state.py
│   │   ├── prompts.py
│   │   ├── tools.py
│   │   └── chains.py
│   └── main.py
├── alembic/
│   ├── env.py
│   └── versions/
├── tests/
│   ├── test_books.py
│   ├── test_auth.py
│   └── conftest.py
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
├── .env.example
├── README.md
└── .gitignore
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get access/refresh tokens
- `POST /api/v1/auth/refresh` - Refresh access token

### Books (Protected)
- `GET /api/v1/books/` - List books (with pagination and filtering)
- `POST /api/v1/books/` - Create a new book
- `GET /api/v1/books/{id}` - Get a book by ID
- `PUT /api/v1/books/{id}` - Update a book
- `DELETE /api/v1/books/{id}` - Delete a book

### Health
- `GET /health` - Health check endpoint
- `GET /` - Welcome message

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PROJECT_NAME` | Project name | "Book Management API" |
| `VERSION` | API version | "0.1.0" |
| `API_V1_STR` | API version prefix | "/api/v1" |
| `POSTGRES_SERVER` | PostgreSQL host | "localhost" |
| `POSTGRES_USER` | PostgreSQL user | "postgres" |
| `POSTGRES_PASSWORD` | PostgreSQL password | "postgres" |
| `POSTGRES_DB` | PostgreSQL database | "bookdb" |
| `POSTGRES_PORT` | PostgreSQL port | "5432" |
| `REDIS_HOST` | Redis host | "localhost" |
| `REDIS_PORT` | Redis port | "6379" |
| `REDIS_PASSWORD` | Redis password | "" |
| `REDIS_DB` | Redis database | "0" |
| `SECRET_KEY` | Secret key for JWT | (required) |
| `ALGORITHM` | JWT algorithm | "HS256" |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiration | 30 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiration | 7 |
| `BACKEND_CORS_ORIGINS` | CORS origins | [] |
| `LOG_LEVEL` | Log level | "INFO" |
| `RATE_LIMIT_PER_MINUTE` | Requests per minute | 60 |

## License

MIT

## Contact

Your Name - your.email@example.com

Project Link: https://github.com/yourusername/book-management-api