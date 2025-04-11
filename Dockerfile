# Use official Python image as a base
FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . /app/

EXPOSE 8000

# Run migrations ( alembic) and start the FastAPI server with Uvicorn 
CMD ["sh", "-c", "alembic upgrade head && python -m app.main"]
# CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]

# CMD ["sh", "-c", "alembic upgrade head &&uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
