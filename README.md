# Stormy - LangChain Weather Agent

[![ChatBot-workflow](https://github.com/DavidNavarroSaiz/langchain_weather_agent/actions/workflows/ci.yml/badge.svg)](https://github.com/DavidNavarroSaiz/langchain_weather_agent/actions/workflows/ci.yml)
![Stormy Weather Agent](https://img.shields.io/badge/Stormy-Weather%20Agent-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red)
![LangChain](https://img.shields.io/badge/LangChain-Latest-orange)
![MongoDB](https://img.shields.io/badge/MongoDB-Latest-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

A powerful weather assistant built with LangChain, FastAPI, and Streamlit. Stormy provides accurate weather information through a conversational interface, with persistent memory and advanced prompt management.

## 🌟 Features

- **🤖 AI-powered Weather Assistant**: Leverages LangChain and OpenAI to provide intelligent weather information
- **🔐 User Authentication**: Secure JWT-based authentication system
- **💾 Persistent Memory**: MongoDB-based conversation history for personalized experiences
- **🌐 RESTful API**: FastAPI backend with comprehensive documentation
- **📱 Streamlit UI**: Beautiful and responsive chat interface
- **📝 Prompt Management**: Advanced prompt management with LangSmith integration
- **🔄 Docker Support**: Easy deployment with Docker and docker-compose
- **📊 LangSmith Monitoring**: Track and analyze agent performance
- **🌦️ OpenWeather Integration**: Real-time weather data and forecasts

## 🏗️ Architecture

The Stormy Weather Agent follows a modern microservices architecture:

```
graph TD;

    %% User Interaction
    User["🌤️ User Inputs Query"] -->|Sends Query| StreamlitUI["📱 Streamlit Chat UI"];
    
    %% Backend API
    StreamlitUI -->|POST /api/chat| FastAPI["🚀 FastAPI Backend"];
    
    %% Authentication
    FastAPI -->|Validates JWT Token| Auth["🔐 User Authentication"];
    Auth -->|User Verified| FastAPI;

    %% Agent Execution
    FastAPI -->|Passes Query| AgentExecutor["🤖 LangChain AgentExecutor"];
    
    %% Decision Making
    AgentExecutor -->|Selects Tool| ToolDecision{"🤔 Decide Tool?"};
    
    ToolDecision -->|Weather Now?| GetCurrentWeather["🌦️ get_current_weather"];
    ToolDecision -->|Forecast?| GetForecast["📅 get_weather_forecast"];

    %% Tool Execution
    GetCurrentWeather -->|Fetches Data| OpenWeatherAPI["🌍 OpenWeather API"];
    GetForecast -->|Fetches Forecast| OpenWeatherAPI;

    %% Prompt Cache System
    AgentExecutor -->|Fetches Prompt| PromptCache["📝 PromptCache"];
    PromptCache -->|Checks Cache| CheckCache{"📂 Prompt in Cache?"};
    
    CheckCache -->|Yes| UseCachedPrompt["✅ Use Cached Prompt"];
    CheckCache -->|No| FetchFromHub["🔄 Fetch from LangChain Hub / LangSmith"];
    
    FetchFromHub -->|Retrieve Prompt| PromptCache;
    PromptCache -->|Update Cache| UseCachedPrompt;
    
    UseCachedPrompt -->|Send to Agent| AgentExecutor;

    %% Memory & Context
    AgentExecutor -->|Stores Chat History| MongoDBMemory["💾 MongoDB Chat Memory"];
    MongoDBMemory -->|Retrieves Context| AgentExecutor;

    %% LangSmith Tracking
    subgraph "📊 LangSmith Monitoring"
        AgentExecutor -->|Track Query| LangSmithTrack["📈 Log to LangSmith"];
        GetCurrentWeather -->|Track Call| LangSmithTrack;
        GetForecast -->|Track Call| LangSmithTrack;
        FetchFromHub -->|Track Prompt Fetch| LangSmithTrack;
        UseCachedPrompt -->|Track Cache Usage| LangSmithTrack;
    end
    
    %% Response Back
    PromptCache -->|Formatted Response| FastAPI;
    FastAPI -->|Returns Response| StreamlitUI;
    StreamlitUI -->|Displays Response| User;
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- MongoDB
- OpenAI API Key
- OpenWeather API Key
- LangSmith API Key (optional, for prompt management and tracing)

### Environment Setup

Create a `.env` file with the following variables:

```
# OpenAI API
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo-0125

# OpenWeather API
OPENWEATHER_API_KEY=your_openweather_api_key
OPENWEATHER_BASE_URL=https://api.openweathermap.org
OPENWEATHER_GEO_URL=http://api.openweathermap.org/geo/1.0
OPENWEATHER_MAPS_URL=https://tile.openweathermap.org/map

# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DB=weather_agent_db
MONGO_COLLECTION=chat_history

# LangSmith
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=weather_agent

# JWT Authentication
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Installation

#### Option 1: Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/stormy-weather-agent.git
   cd stormy-weather-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the FastAPI server:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

4. In a separate terminal, start the Streamlit UI:
   ```bash
   streamlit run streamlit_app.py
   ```

#### Option 2: Docker Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/stormy-weather-agent.git
   cd stormy-weather-agent
   ```

2. Start the services using Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. Access the applications:
   - FastAPI: http://localhost:8080/docs
   - Streamlit UI: http://localhost:8501

## 🔧 System Components

### 1. FastAPI Backend (`app.py`)

The FastAPI backend provides RESTful endpoints for:
- User authentication and management
- Weather agent interaction
- Chat history management
- Prompt management

### 2. Streamlit UI (`streamlit_app.py`)

A user-friendly chat interface that:
- Handles user authentication
- Displays chat history
- Sends queries to the backend
- Shows formatted responses

### 3. Weather Agent (`weather_agent.py`)

The core LangChain agent that:
- Processes user queries
- Decides which tools to use
- Fetches weather data
- Formats responses

### 4. OpenWeather API Wrapper (`openweather_api.py`)

A comprehensive wrapper for the OpenWeather API that:
- Gets geolocation data
- Fetches current weather
- Retrieves weather forecasts
- Formats weather data into readable responses

### 5. MongoDB Memory Handler (`memory_handler.py`)

Manages conversation history using MongoDB:
- Stores chat messages
- Retrieves context for the agent
- Maintains user-specific conversation history

### 6. Prompt Cache System (`prompt_cache.py`)

Advanced prompt management with LangSmith integration:
- Caches prompts locally
- Fetches prompts from LangChain Hub
- Updates prompts when needed
- Creates default prompts when necessary

## 📚 API Documentation

### User Management

- `POST /signup` - Create a new user account
- `POST /token` - Login and get access token
- `DELETE /users/{username}` - Delete a user account

### Weather Agent

- `POST /api/chat` - Send a query to the weather agent

### Chat History

- `GET /chat-history` - Get chat history for the current user
- `DELETE /chat-history` - Delete chat history for the current user

### Prompt Management

- `GET /prompts` - List all prompts in the cache
- `GET /prompts/{prompt_id}` - Get details of a specific prompt
- `POST /prompts/update-all` - Update all prompts in the cache

## 🔍 Usage Examples

### User Registration

```bash
curl -X 'POST' \
  'http://localhost:8000/signup' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "john_doe",
  "password": "secure_password123"
}'
```

### User Login

```bash
curl -X 'POST' \
  'http://localhost:8000/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=john_doe&password=secure_password123'
```

### Weather Query

```bash
curl -X 'POST' \
  'http://localhost:8000/api/chat' \
  -H 'Authorization: Bearer your_access_token' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "What'\''s the weather like in London today?"
}'
```

### Get Chat History

```bash
curl -X 'GET' \
  'http://localhost:8000/chat-history?limit=10' \
  -H 'Authorization: Bearer your_access_token'
```

## 🧠 Prompt Management

The application includes a sophisticated prompt management system that integrates with LangSmith:

### Prompt Cache System

The `PromptCache` class provides a singleton instance for managing cached prompts:

- **Initialization**: Automatically pulls prompts from LangSmith on startup
- **Caching**: Stores prompts locally to reduce API calls
- **Updates**: Allows refreshing prompts from LangSmith
- **Fallbacks**: Creates default prompts when needed

### Using LangSmith for Prompts

Benefits of using LangSmith for prompt management:

1. **Version Control**: Track changes to prompts over time
2. **Centralized Management**: Manage prompts from a central location
3. **Collaboration**: Share prompts with team members
4. **Performance Monitoring**: Track prompt effectiveness

## 📊 LangSmith Monitoring

The system integrates with LangSmith for comprehensive monitoring:

- **Query Tracking**: Log all user queries
- **Tool Usage**: Monitor which tools are being used
- **Response Analysis**: Analyze agent responses
- **Performance Metrics**: Track response times and success rates

## 🐳 Docker Deployment

The application is containerized with Docker for easy deployment:

- **Multi-Container Setup**: Separate containers for API, Streamlit, and MongoDB
- **Environment Variables**: Configured through docker-compose.yml
- **Networking**: Internal network for secure communication
- **Persistence**: Volume mounting for MongoDB data

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt hashing for user passwords
- **Role-Based Access**: Endpoint protection based on user roles
- **Environment Variables**: Sensitive information stored in environment variables

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [LangChain](https://github.com/langchain-ai/langchain) for the agent framework
- [OpenAI](https://openai.com/) for the language model
- [OpenWeather](https://openweathermap.org/) for weather data
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- [Streamlit](https://streamlit.io/) for the UI framework
- [MongoDB](https://www.mongodb.com/) for the database

## 🧪 Testing and CI/CD

- **🔄 Continuous Integration**: Automated testing and linting with GitHub Actions
- **🧪 Comprehensive Test Suite**: Unit and integration tests for all components
- **📊 Code Coverage**: Detailed code coverage reports
- **🐳 Docker Testing**: Automated Docker build testing
- **🔍 Quality Assurance**: Code quality checks with Black and isort

The project includes a comprehensive test suite built with pytest. Tests cover all major components including the weather agent, API endpoints, user management, and memory handling.

### Running Tests

To run the tests locally:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests with coverage report
pytest --cov=.

# Run specific test files
pytest tests/test_weather_agent.py

# Run tests with specific markers
pytest -m unit  # Run only unit tests
pytest -m integration  # Run only integration tests
```

### Continuous Integration

The project uses GitHub Actions for continuous integration. The CI pipeline:

1. Runs on multiple Python versions (3.9, 3.10)
2. Sets up a MongoDB service container for integration tests
3. Installs all dependencies
4. Runs linting checks with Black and isort
5. Executes the test suite with coverage reporting
6. Builds the Docker image to ensure it works correctly

The CI workflow is defined in `.github/workflows/ci.yml`.
