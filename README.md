# LangChain Weather Agent API

A FastAPI-based REST API for interacting with a LangChain-powered weather agent. This application provides endpoints for user management, chat interactions with a weather agent, and chat history management.

## Features

- 🤖 AI-powered weather assistant using LangChain and OpenAI
- 🔐 User authentication with OAuth2
- 💾 Persistent conversation memory using MongoDB
- 🌐 RESTful API with FastAPI
- 📝 Comprehensive API documentation with Swagger UI

## Setup

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Configure your `.env` file with the following variables:
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
   ```

3. Start the API server:
   ```
   python app.py
   ```
   
   Or with uvicorn directly:
   ```
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

4. Access the API documentation at http://localhost:8000/docs

## API Usage

### User Management

#### Create a new user

```bash
curl -X 'POST' \
  'http://localhost:8000/signup' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "john_doe",
  "password": "secure_password123"
}'
```

#### Login and get access token

```bash
curl -X 'POST' \
  'http://localhost:8000/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=john_doe&password=secure_password123'
```

### Weather Agent Interaction

#### Send a query to the weather agent

```bash
curl -X 'POST' \
  'http://localhost:8000/api/chat' \
  -H 'Authorization: Bearer your_access_token' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "What'\''s the weather like in London today?"
}'
```

> **Note**: Authentication is required for this endpoint. The user's token is used to identify the user and maintain conversation context across multiple queries.

### Chat History Management

#### Get chat history

```bash
curl -X 'GET' \
  'http://localhost:8000/chat-history?limit=10' \
  -H 'Authorization: Bearer your_access_token'
```

#### Delete chat history

```bash
curl -X 'DELETE' \
  'http://localhost:8000/chat-history' \
  -H 'Authorization: Bearer your_access_token'
```

## API Endpoints

### User Management
- `POST /signup` - Create a new user account
- `POST /token` - Login and get access token
- `DELETE /users/{username}` - Delete a user account

### Weather Agent
- `POST /api/chat` - Send a query to the weather agent

### Chat History
- `GET /chat-history` - Get chat history for the current user
- `DELETE /chat-history` - Delete chat history for the current user

## OpenWeather API Wrapper

This project includes a Python wrapper for the OpenWeather API that uses environment variables for configuration.

### Available Methods

- `get_geolocation(city_name, country_code=None, state_code=None, limit=1)`: Get geographic coordinates for a location
- `get_current_weather(lat, lon, units="metric", lang="en")`: Get current weather for coordinates
- `get_forecast(lat, lon, units="metric", lang="en", cnt=40)`: Get weather forecast
- `get_weather_map_url(layer, z, x, y)`: Get URL for weather map tiles