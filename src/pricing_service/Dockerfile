# Use a lightweight official Python image as the base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
# This step is cached, speeding up rebuilds if app.py changes but deps don't
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY app.py .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application using uvicorn
# The container will run with 1 worker and log to stdout
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]