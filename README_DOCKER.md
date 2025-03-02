# Docker Setup for Weather Agent

This document provides instructions for running the Weather Agent application using Docker and Docker Compose.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Environment Variables

Before running the application, make sure you have the following environment variables set:

- `OPENWEATHER_API_KEY`: Your OpenWeather API key
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: The OpenAI model to use (e.g., "gpt-4o-mini")
- `LANGSMITH_TRACING`: Set to "true" to enable LangSmith tracing
- `LANGSMITH_ENDPOINT`: LangSmith API endpoint
- `LANGSMITH_API_KEY`: Your LangSmith API key
- `LANGSMITH_PROJECT`: LangSmith project name

You can set these environment variables in your shell or create a `.env` file in the project root.

## Running the Application

1. Build and start the containers:

```bash
docker-compose up -d
```

2. Access the applications:

- FastAPI: http://localhost:8000
- FastAPI Documentation: http://localhost:8000/docs
- Streamlit UI: http://localhost:8501

3. Stop the containers:

```bash
docker-compose down
```

## Services

The Docker Compose setup includes the following services:

- **MongoDB**: Database for storing chat history and user data
- **FastAPI**: Backend API for the Weather Agent
- **Streamlit**: Frontend UI for interacting with the Weather Agent

## Volumes

- **mongodb_data**: Persistent volume for MongoDB data

## Networks

- **weather_agent_network**: Internal network for communication between services

## Troubleshooting

If you encounter any issues:

1. Check the logs:

```bash
docker-compose logs
```

2. For specific service logs:

```bash
docker-compose logs [service_name]
```

Where `[service_name]` can be `mongodb`, `api`, or `streamlit`.

3. To rebuild the containers:

```bash
docker-compose up -d --build
```

## Development

For development purposes, you can run individual services:

```bash
docker-compose up mongodb -d  # Run only MongoDB
docker-compose up api -d      # Run only the API
docker-compose up streamlit -d # Run only the Streamlit app
``` 