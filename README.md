# User-Role-Management
Using this repository, you can have a user and role management system. You need to run init_db.py to seed the database for initial use. It has apis for CRUD operations for user management, role and permission management. Additionally it also has data-source management for storing kibana and grafana sources. 

## Overview

It is built using FastAPI, a modern, fast (high-performance), and async-ready web framework for building APIs in Python. This README provides the necessary steps to set up, run, and maintain the project locally or via Docker.

## Prerequisites

1. Docker installed on your system.
2. Python installed on your system (if you wish to run the project locally without Docker).
3. Ensure `pip` (Python's package installer) is available if you plan to run the project locally.

## Installation and Setup

### Option 1: Run the Application Using Docker

To run the project in a containerized environment, Docker is required. Follow these steps:

1. **Clone and Navigate to the Project Directory**

   Navigate to the project directory where the API resides:

   ```bash
   cd user-role-management
   ```

2. **Copy the `.env.example` File to `.env`**

   The `.env` file contains sensitive environment variables, including database credentials and JWT secrets. Copy the `.env.example` to `.env` and update it accordingly:

   ```bash
   cp .env.example .env
   ```

   Open `.env` and update the necessary credentials:

   - `DATABASE_HOST`: Set this to `host.docker.internal` if using MySQL on the host machine, or provide your database server's hostname (e.g., AWS RDS endpoint).
   - `DATABASE_PORT`: Default MySQL port is `3306`. Update this if your database is running on a different port.
   - `DATABASE_USER`: Set this to the MySQL username.
   - `DATABASE_PASSWORD`: Set this to the MySQL password.
   - `DATABASE_NAME`: Set this to the MySQL database name.

   Example `.env`:

   ```env
   DATABASE_HOST=host.docker.internal
   DATABASE_PORT=3306
   DATABASE_NAME=anveshan
   DATABASE_USER=root
   DATABASE_PASSWORD=my_secret_password
   ```

3. **Build and Run the Docker Containers**

   With the `.env` file set up, build and run the Docker containers:

   ```bash
   docker-compose up --build
   ```

   This will start the API server and connect it to your MySQL database. The application will now be accessible at `http://localhost:8000`.

### Option 2: Run the Application Locally Without Docker

If you prefer to run the application locally without Docker, follow these steps:

1. **Install `uv`**

   Install `uv`, the Python package manager, in your global Python environment:

   ```bash
   pip install uv
   ```

2. **Clone and Navigate to the Project Directory**

   Navigate to the project directory where the API resides:

   ```bash
   cd user-role-management
   ```

3. **Create a Virtual Environment**

   Set up a virtual environment to isolate dependencies:

   ```bash
   uv venv
   ```

   Activate the virtual environment:

   On Windows:

   ```bash
   .venv\Scripts\activate
   ```

   On Linux/MacOS:

   ```bash
   source .venv/bin/activate
   ```

4. **Install Dependencies**

   Install all required packages specified in `requirements.txt`:

   ```bash
   uv pip install -r requirements.txt
   ```

5. **Run Database Migrations**

   Apply the database migration files:

   ```bash
   alembic upgrade head
   ```

6. **Start the Application**

   Run the application using `uvicorn`:

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

   The application will now be accessible at `http://0.0.0.0:8000`.

## Development Notes

- **Use `--reload` during development** to auto-reload the application on code changes.
- Make sure to **activate the virtual environment** every time you start working on the project (if running locally).
- If using Docker, **ensure MySQL is accessible** from the container either by setting `DATABASE_HOST` to `host.docker.internal` for local MySQL or providing the external hostname for a remote database.

---
