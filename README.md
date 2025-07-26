# RAG Chainlit API

A Retrieval-Augmented Generation (RAG) chatbot API built with FastAPI and Chainlit, designed for AI and Data Governance policy assistance.

## Features

- **FastAPI Backend**: RESTful API for chat functionality
- **Chainlit Frontend**: Interactive chat interface
- **RAG Implementation**: Uses LangChain with ChromaDB for document retrieval
- **LLM Integration**: Powered by Llama-2-7b-chat model
- **Vector Search**: Semantic search using HuggingFace embeddings

## Project Structure

```
├── api.py              # FastAPI server with chat endpoint
├── chainlet.py         # Chainlit chat interface
├── rag.py             # RAG implementation with LangChain
├── chroma_db/         # Vector database (ChromaDB)
├── requirements.txt   # Python dependencies (for Railway deployment)
├── environment.yml    # Conda environment specification
├── railway.yaml       # Railway deployment configuration
├── Dockerfile         # Docker configuration
├── start.sh           # Linux/Mac startup script (Conda)
├── start.bat          # Windows startup script (Conda)
└── README.md          # This file
```

## Local Development

### Prerequisites

- Python 3.9+
- Anaconda or Miniconda
- Git
- Sufficient RAM (4GB+ recommended for Llama-2-7b)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd Rag_Chainlet_API
```

2. Create conda environment from environment.yml:
```bash
conda env create -f environment.yml
```

3. Activate the environment:
```bash
conda activate rag_chainlit_env
```

### Running the Application

#### Option 1: Using startup scripts
- **Linux/Mac**: `./start.sh`
- **Windows**: `start.bat`

#### Option 2: Manual startup
1. **Activate conda environment:**
```bash
conda activate rag_chainlit_env
```

2. **Start the FastAPI server:**
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

3. **In another terminal, start Chainlit:**
```bash
conda activate rag_chainlit_env
chainlit run chainlet.py
```

3. **Access the application:**
- API: http://localhost:8000
- Chainlit Interface: http://localhost:8001

## API Endpoints

### Health Check
- **GET** `/` - Returns service health status

### Chat
- **POST** `/chat`
  ```json
  {
    "question": "Your question here"
  }
  ```

## Deployment

### Railway Deployment

1. **Connect to Railway:**
   - Create account at [railway.app](https://railway.app)
   - Connect your GitHub repository

2. **Automatic Deployment:**
   - Railway will detect the `railway.yaml` configuration
   - Deployment will start automatically

3. **Environment Variables:**
   - No additional environment variables required
   - Model caching is handled automatically

### Docker Deployment

```bash
docker build -t rag-chainlit-api .
docker run -p 8000:8000 rag-chainlit-api
```

## Configuration

### Model Configuration
- **LLM**: meta-llama/Llama-2-7b-chat-hf
- **Embeddings**: BAAI/bge-base-en-v1.5
- **Vector DB**: ChromaDB with local persistence

### Resource Requirements
- **Memory**: 4GB+ (for model loading)
- **CPU**: 2+ cores recommended
- **Storage**: 15GB+ (for model downloads)

## Architecture

The application consists of three main components:

1. **FastAPI Server** (`api.py`): Handles HTTP requests and responses
2. **RAG Engine** (`rag.py`): Processes queries using retrieval and generation
3. **Chainlit Interface** (`chainlet.py`): Provides user-friendly chat interface

## Troubleshooting

### Common Issues

1. **Memory Issues**: Reduce model size or use quantization
2. **Slow Loading**: Models are downloaded on first run
3. **Port Conflicts**: Change ports in configuration files

### Model Download
Models are downloaded automatically on first run. This may take time depending on internet speed.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the GitHub repository.
