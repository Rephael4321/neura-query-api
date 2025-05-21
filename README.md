# Neura Query API – Backend

A FastAPI-based backend that powers Neura Query, translating natural language into SQL, executing queries, and returning results from user databases.

---

## Important note!

This repo is synced with the [neura-query-frontend](https://github.com/Rephael4321/neura-query) repo.
You can set it up, and setup the fronted for a nice GUI. If you are encountering a problem with the setup or with the usage of this project, please let me know with a pull request.

---

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [License](#license)
- [Author](#author)

---

## Overview

Neura Query enables users to query SQL databases using natural language. This backend serves as the core API that handles:

- User authentication (sign in / sign up)
- Translating natural language queries into SQL
- Executing SQL queries against the user's connected database
- Returning clean, structured results to the frontend

Built with **FastAPI** and running via **Uvicorn**, this backend is the engine behind the Neura Query frontend interface.

---

## System Architecture

The Neura Query API functions as the backend gateway for all user interactions.

- Receives API requests from the frontend
- Handles authentication and validation
- Sends natural language queries to the **Server Manager** over a **Kafka** (Kraft) messaging system
- The **Server Manager** performs the AI-driven translation and query logic
- Communicates with a **PostgreSQL** database
- Returns query results to the frontend in a structured format

---

## Project Structure

This structure is concise, and display only the most important partial structure of the project.

- docker-compose.yaml # Config file for docker-compose
- initialize_db.py # Specialized script for initializing Neura Query DB. Used only once at startup. WARNING: It erases all data!
- fastapi/ # Docker container used as the API.
- manager/ # Docker container used as the Server Manager.
- shared/ # Those are files that are crucial for both, fastapi and manager. Those files has to be synced in both services.

---

## Prerequisites

- [Python](https://www.python.org/)
- [Docker](https://www.docker.com/)
- [OpenAI](https://platform.openai.com/api-keys/)

---

## Quick Start
### 1. Clone the repo:

```bash
git clone https://github.com/Rephael4321/neura-query-api
cd neura-query
```

### 2. Set up environment variables in a .env file:

```env
# JWT Configurations
SECRET_KEY=jwt_key
ALGORITHM=jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES=jwt_expiration_time

# PostgreSQL Configurations
DB_HOST=postgres_name
POSTGRES_USER=postgres_username
POSTGRES_PASSWORD=postgres_password

# FastAPI Configurations
DEV_CORS_ADDRESS=gui_address_dev_mode
PROD_CORS_ADDRESS=gui_address_prod_mode
PORT=api_port

# OpenAI Key
OPENAI_API_KEY=open_ai_key
```

### 3. Run the development server:

```bash
docker-compose up --build
```

---

## License
```pgsql
GNU AFFERO GENERAL PUBLIC LICENSE
Version 3, 19 November 2007
```

---

## Author

Rephael Sintes, a.k.a rephael4321
  - Portfolio: [https://rephael4321.com](https://rephael4321.com)
  - GitHub: [https://github.com/Rephael4321](https://github.com/Rephael4321)
  - LinkedIn: [https://linkedin.com/in/rephael-sintes-833177196](https://linkedin.com/in/rephael-sintes-833177196)
