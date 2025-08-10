# Requirements vs Design Comparison API

A FastAPI-based backend service that provides semantic analysis between requirements and design documents, with LLM-powered feedback and conversational chat capabilities.

## Features

- **Semantic Analysis**: Compare requirements against design documents using TF-IDF and cosine similarity
- **File Upload Support**: Parse JSON, YAML, and text documents
- **LLM Integration**: Get intelligent feedback using OpenAI GPT models
- **Conversational Chat**: Interactive discussions with conversation history
- **RESTful API**: Clean, well-documented API endpoints
- **Async Processing**: Non-blocking request handling

## Architecture

```
fastapi-app/
├── app/
│   ├── main.py              # FastAPI application
│   ├── services/
│   │   ├── llm_service.py   # OpenAI integration
│   │   └── chat_service.py  # Conversation management
├── requirements.txt         # Dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Installation

1. **Clone and navigate to the project:**
   ```bash
   cd fastapi-app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install spaCy model:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

5. **Run the application:**
   ```bash
   python -m app.main
   ```

## API Endpoints

### Document Analysis
- `POST /api/upload-requirements` - Upload requirements file
- `POST /api/upload-design` - Upload design file
- `POST /api/analyze` - Perform semantic analysis

### LLM Integration
- `POST /api/chat` - Start/continue conversation
- `GET /api/chat/{conversation_id}/history` - Get conversation history
- `POST /api/analyze/llm-feedback` - Get LLM-powered feedback

### Health Check
- `GET /health` - Application health status

## Usage Examples

### 1. Upload and Analyze Documents

```bash
# Upload requirements
curl -X POST "http://localhost:8000/api/upload-requirements" \
  -F "file=@requirements.json"

# Upload design
curl -X POST "http://localhost:8000/api/upload-design" \
  -F "file=@design.yaml"

# Analyze
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": ["User must be able to login", "System should send email notifications"],
    "design": ["Login page with username/password fields", "Email service integration"],
    "threshold": 0.3
  }'
```

### 2. Start Conversation with LLM

```bash
# Start new conversation
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the main gaps in my requirements coverage?",
    "conversation_id": null
  }'

# Continue conversation
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How can I improve the email notification design?",
    "conversation_id": "your-conversation-id"
  }'
```

### 3. Get LLM Feedback

```bash
curl -X POST "http://localhost:8000/api/analyze/llm-feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": ["req1", "req2"],
    "design": ["design1", "design2"],
    "analysis_results": [...]
  }'
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `DEBUG` | Enable debug mode | `True` |
| `SECRET_KEY` | Application secret key | Generate random |
| `CORS_ORIGINS` | Allowed CORS origins | `*` |

## Development

### Running with hot reload:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Testing:
```bash
pytest tests/
```

## Migration from Streamlit

This FastAPI version replaces the original Streamlit app (`hi.py`) with:
- **Better performance**: Async request handling
- **API-first design**: Easy integration with any frontend
- **Scalability**: Can handle multiple concurrent users
- **LLM integration**: Conversational AI capabilities
- **Conversation history**: Persistent chat sessions

## Future Enhancements

- [ ] Database integration for persistent storage
- [ ] WebSocket support for real-time chat
- [ ] Advanced NLP models (BERT, etc.)
- [ ] User authentication
- [ ] Rate limiting
- [ ] API versioning
- [ ] Docker containerization
- [ ] Frontend React application

## License

MIT License
