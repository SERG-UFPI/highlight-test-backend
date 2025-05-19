# Highlight Test Backend

## Overview
The **Highlight Test Backend** application is designed to handle various tasks related to software repository analysis and insights generation. It provides functionality for repository cloning, commit extraction, time series generation, metric calculation, and co-evolution analysis.

## Features
- **Repository Cloning**: Clone repositories for analysis.
- **Commit Extraction**: Extract and analyze commit data.
- **Time Series Generation**: Generate time series data for repository metrics.
- **Metric Calculation**: Calculate various metrics such as code distribution, test coverage, and maintenance activities.
- **Co-Evolution Analysis**: Analyze the co-evolution of code and tests.
- **Insights Generation**: Provide insights into repository health and development practices.

## Technologies Used
The project leverages the following technologies:
- **Backend**: Python
- **Frameworks**: FastAPI

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/SERG-UFPI/highlight-test-backend.git
   cd highlight-test-backend
   
2. Install the dependencies from requirements.txt:
    ```bash
    pip install -r requirements.txt

## Environment Variables

The application requires the following environment variables to be set. These can be configured in a `.env` file in the root directory of the project:

- **SERVER_BASE_URL**: Base URL for the server (e.g., `http://localhost:8000`).
- **AUTH_SECRET_KEY**: Secret key for authentication.
- **AUTH_ALGORITHM**: Algorithm used for token generation (e.g., `HS256`).
- **AUTH_ACCESS_TOKEN_EXPIRE_MINUTES**: Expiration time for access tokens in minutes.
- **SQLALCHEMY_DATABASE_URL**: Database connection string (e.g., `postgresql://<user>:<password>@<host>:<port>/<database>?options=-csearch_path=<schema>`).
- **CELERY_BROKER_URL**: URL for the Celery message broker.
- **CELERY_BACKEND**: Backend URL for Celery.
- **GITHUB_CLIENT_ID**: GitHub OAuth client ID.
- **GITHUB_CLIENT_SECRET**: GitHub OAuth client secret.
- **GITHUB_REDIRECT_URI**: Backend URL for GitHub OAuth callback.
- **GITHUB_REDIRECT_FRONTEND**: Frontend URL for GitHub OAuth callback.
- **FRONTEND_URL**: URL for the frontend application.
- **SERVER_HOST**: Host for the server (e.g., `127.0.0.1`).
- **SERVER_PORT**: Port for the server (e.g., `8000`).
- **GEMINI_API_KEY**: API key for external services.

Ensure these variables are properly set before running the application.