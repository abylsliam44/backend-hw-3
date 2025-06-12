# Personal Finance Manager with AI Agents

A full-stack web application for managing personal finances with integrated AI conversation agents powered by Google's Gemini API.

## Features

- Personal finance management with transaction and category tracking
- User authentication with JWT
- Real-time AI conversation between two Gemini-powered agents
- WebSocket-based communication
- PostgreSQL database integration
- Docker containerization
- Render.com deployment support

## Tech Stack

### Backend
- FastAPI
- PostgreSQL
- SQLAlchemy
- Google Gemini AI
- WebSockets
- JWT Authentication

### Frontend
- React
- Material-UI
- WebSocket client
- TypeScript

## Local Development

### Prerequisites
- Docker and Docker Compose
- Node.js 16+
- Python 3.9+
- PostgreSQL 13+

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

3. Update the `.env` file with your credentials:
```
POSTGRES_DB=finance_db
POSTGRES_USER=finance_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql://finance_user:your_password@db:5432/finance_db
GOOGLE_API_KEY=your_gemini_api_key
```

### Running with Docker

Start all services:
```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Deployment to Render.com

### Prerequisites
1. Create a Render.com account
2. Set up a PostgreSQL database on Render.com
3. Have your Google Gemini API key ready

### Deployment Steps

1. Fork/push this repository to your GitHub account

2. On Render.com:
   - Create a new "Blueprint" instance
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` configuration

3. Configure environment variables:
   - Set `DATABASE_URL` to your Render PostgreSQL instance URL
   - Set `GOOGLE_API_KEY` to your Gemini API key
   - Set `POSTGRES_PASSWORD` to a secure password
   - Other variables will be automatically configured

4. Deploy:
   - Render will automatically build and deploy both frontend and backend
   - Monitor the deployment logs for any issues

## API Documentation

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## WebSocket Endpoints

- `/ws/conversation` - Real-time AI agent conversation
- Messages include:
  - Agent name
  - Message content
  - Timestamp
  - Message type (message/error/end)

## Development Notes

### Local Testing
```bash
# Run tests
cd backend
pytest

# Run linting
flake8
black .
```

### Database Migrations
```bash
# Generate migrations
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 