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

# Project Structure

The repository is organized as follows:

- **`app/`**: Contains the main application code.
  - **`helpers/`**: Utility functions for data processing and analysis.
  - **`routers/`**: API endpoints grouped by functionality.
  - **`tasks/`**: Background tasks for operations like cloning repositories and generating metrics.
  - **`main.py`**: Entry point for the FastAPI application.

- **`tests/`**: Unit and integration tests for the application.

- **`external/`**: Contains external services used by the application that are essential to its core functionality.

- **`Dockerfile.worker`**: Dockerfile for setting up the worker environment.

- **`requirements.txt`**: Python dependencies required for the project.

- **`README.md`**: Documentation for the project.

- **`.env`**: Environment variables configuration file.

## Supported Environments

The tool has been built and tested to run locally on both Windows and Linux environments. Ensure the necessary dependencies and environment variables are properly configured for your operating system.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/SERG-UFPI/highlight-test-backend.git
   cd highlight-test-backend
   
2. Install the dependencies from requirements.txt:
    ```bash
    pip install -r requirements.txt
   ```

## Additional Requirements
If you are running the application on a non-Windows environment, you need to install `cloc` as it is required for certain functionalities. You can install it using the following command:
   ```bash
   apt-get update && apt-get install -y cloc
   ```

## Environment Variables

The application requires the following environment variables to be set. These can be configured in a `.env` file in the root directory of the project:

- **SERVER_BASE_URL**: Base URL for the server (e.g., `http://localhost:8000`).
- **SERVER_RESULTS_PATH**: Path where the server will store result files (e.g., `/var/home/results`).
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

**The frontend for the Highlight Test Code tool is available at:**  
[https://github.com/SERG-UFPI/highlight-test-frontend](https://github.com/SERG-UFPI/highlight-test-frontend)

**If you do not wish to install and configure the tool locally, you can access the Highlight Test Code platform directly via the web:**  
[https://highlight-test-frontend.vercel.app](https://highlight-test-frontend.vercel.app)

## Related Publication
<a id="1" href="http://dx.doi.org/10.1002/smr.70035">[1]</a> Miranda, Charles, et al. "Test Co-Evolution in Software Projects: A Large-Scale Empirical Study." Journal of Software: Evolution and Process. 37, 7 (2025), e70035.<br>
<a id="2" href="https://zenodo.org/records/15871617">[2]</a> Miranda, Charles, et al. "Highlight Test Code: Visualizing the Co-Evolution of Test and Production Code in Software Repositories." Simpósio Brasileiro de Engenharia de Software (2025).
