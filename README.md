# 🏇 Horse Racing Prediction System

A production-grade ML-powered horse racing analysis platform with:
- Real-time race predictions using PyTorch & XGBoost
- Interactive chat interface powered by LLMs and RAG
- Comprehensive backtesting engine
- Beautiful modern UI

## Tech Stack
- **Frontend**: React 18, Tailwind CSS, Framer Motion
- **Backend**: Java 25 (Spring Boot), Python 3.12 (FastAPI)
- **ML**: PyTorch, scikit-learn, XGBoost
- **Database**: PostgreSQL 16
- **AI**: OpenRouter, MCP, RAG (ChromaDB)
- **Deployment**: Railway

## Architecture
[Architecture diagram coming soon]

## Development Setup
See `docs/SETUP.md`

## Project Structure
```
horse-racing-ai/
├── frontend/              # React application
├── backend-api/          # Java Spring Boot REST API
├── ml-service/           # Python ML prediction service
├── mcp-server/           # Model Context Protocol server
├── data-ingestion/       # Racing API data pipeline
├── shared/               # Shared types/utilities
├── docs/                 # Documentation
└── infrastructure/       # Docker, Railway configs
```

## License
MIT
EOF