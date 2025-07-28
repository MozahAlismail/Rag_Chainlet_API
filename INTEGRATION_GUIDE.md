# RAG Chainlit API - Integration Guide

## Overview
The `main.py` file now serves as the **main entry point** for the entire RAG Chainlit API system. It manages both the FastAPI backend and Chainlit frontend in an integrated manner.

## Key Features

### 🚀 Integrated Server Management
- **Automatic API Server**: Starts FastAPI backend automatically when needed
- **Health Monitoring**: Checks if API server is running and starts it if necessary
- **Graceful Shutdown**: Properly manages server lifecycle

### 🎯 Smart Initialization
- **Environment Detection**: Automatically detects Railway vs local development
- **Lazy Loading**: Starts API server only when required
- **Error Handling**: Comprehensive error handling with user-friendly messages

### 💻 Easy Local Development
- **One Command Start**: Run everything with a single script
- **Port Management**: Configurable ports (Chainlit: 8001, API: 8000)
- **Conda Integration**: Works seamlessly with conda environments

## Usage

### Local Development

**Windows:**
```bash
start_main.bat
```

**Linux/Mac:**
```bash
chmod +x start_main.sh
./start_main.sh
```

**Manual Start:**
```bash
conda activate NLPenv
chainlit run main.py --port 8001 --host 0.0.0.0
```

### Railway Deployment
The system automatically detects Railway environment and adjusts behavior accordingly.

### Testing
```bash
python test_integration.py
```

## Configuration

### Environment Variables
- `FASTAPI_URL`: API server URL (default: http://localhost:8000/chat)
- `RAILWAY_ENVIRONMENT`: Set by Railway automatically
- `HUGGINGFACE_API_TOKEN`: For optimized RAG implementation

### Ports
- **Chainlit Interface**: 8001 (configurable)
- **FastAPI Backend**: 8000 (configurable)

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│     main.py     │───▶│   FastAPI API    │───▶│   RAG System    │
│  (Main Entry)   │    │   (api.py)       │    │ (rag.py/opt)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Chainlit Web UI │    │  HTTP Endpoints  │    │   ChromaDB      │
│   (Port 8001)   │    │   (Port 8000)    │    │  Vector Store   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Features

### 🎨 Enhanced User Experience
- **Welcome Messages**: Informative startup messages
- **Loading Indicators**: Visual feedback during processing
- **Error Recovery**: Automatic retry suggestions
- **Status Updates**: Real-time connection status

### 🔧 Developer Experience
- **Automatic Setup**: No manual server management required
- **Debugging Tools**: Comprehensive logging and error messages
- **Testing Suite**: Integration tests for all components
- **Documentation**: Clear setup and usage instructions

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Check if another service is using ports 8000 or 8001
   - Use `netstat -an | findstr "8000"` to check

2. **API Server Won't Start**
   - Check conda environment is activated
   - Verify all dependencies are installed
   - Run `python test_integration.py` for diagnostics

3. **Connection Errors**
   - Wait for API server to fully initialize (can take 30+ seconds)
   - Check firewall settings
   - Verify ChromaDB directory exists

### Logs and Debugging
- Console output shows detailed startup process
- Error messages include troubleshooting steps
- Integration test provides system validation

## Migration from Previous Setup

If you were previously running `api.py` and `main.py` separately:

1. **Stop both services**
2. **Use new startup scripts**: `start_main.bat` or `start_main.sh`
3. **Single URL**: Only http://localhost:8001 needed (for Chainlit)
4. **Automatic management**: No need to manually start API server

The new integrated approach simplifies deployment and development while maintaining all existing functionality.
