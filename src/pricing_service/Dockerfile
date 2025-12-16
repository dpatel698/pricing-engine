# Use a lightweight official Python image as the base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
# We copy the requirements file relative to the new root context
COPY src/pricing_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the trained model from the project's models folder
# The model path is now relative to the project root
COPY src/models/xgb_pricing_model.json /app/models/xgb_pricing_model.json

# Copy the rest of the application code
COPY src/pricing_service/app.py .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application using uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]