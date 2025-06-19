# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY farmpower_backend_v2/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI application code
COPY farmpower_backend_v2/ ./farmpower_backend_v2/

# Copy the FARMPOWER frontend directory
COPY FARMPOWER/ ./FARMPOWER/

# Expose the port the app runs on
EXPOSE 8000

# Run the FastAPI application
# The --host 0.0.0.0 makes the server accessible from outside the container
CMD ["python", "-m", "uvicorn", "farmpower_backend_v2.main:app", "--host", "0.0.0.0", "--port", "8000"] 