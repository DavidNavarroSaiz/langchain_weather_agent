from setuptools import setup, find_packages

setup(
    name="langchain_weather_agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "langchain>=0.1.0",
        "langchain-core>=0.1.10",
        "langchain-openai>=0.0.5",
        "langchain-mongodb>=0.0.1",
        "pymongo>=4.5.0",
        "openai>=1.3.0",
        "pytz>=2023.3",
        "fastapi>=0.104.0",
        "uvicorn>=0.23.2",
        "pydantic>=2.4.2",
        "python-multipart>=0.0.5",
        "python-jose>=3.3.0",
        "streamlit>=1.30.0",
        "bcrypt>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "isort>=5.12.0",
        ],
    },
    python_requires=">=3.9",
) 