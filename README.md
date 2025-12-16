# 🚕 Ride Pricing Service 

This project implements a real-time ride pricing service that predicts the price of a ride based on factors like distance and traffic conditions. It leverages Kafka for asynchronous communication, an XGBoost model for price prediction, and FastAPI for exposing API endpoints. The service consumes ride requests from a Kafka topic, calculates the price using a trained model, and stores the latest prices in-memory. This setup allows for a scalable and responsive pricing system.

🚀 **Key Features**

*   **Real-time Price Prediction:** Predicts ride prices based on real-time data using a trained XGBoost model.
*   **Kafka Integration:** Consumes ride requests from a Kafka topic for asynchronous processing.
*   **API Endpoints:** Provides API endpoints for health checks and testing price predictions.
*   **In-Memory Data Store:** Maintains an in-memory store of the latest prices for quick retrieval.
*   **Dockerized Deployment:** Easily deployable using Docker and Docker Compose.
*   **Model Training Pipeline:** Includes scripts for training and saving the XGBoost model.
*   **Data Generation:** Includes scripts for generating synthetic historical ride data.

🛠️ **Tech Stack**

*   **Backend:**
    *   Python 3.x
    *   FastAPI: Web framework for building the API.
    *   **Message Broker**
    * *   Redpanda (Kafka-compatible)
*   **Containerization:**
    *   Docker

*   **Database:**
    *   PostgreSQL


📦 **Getting Started**

### Prerequisites

*   Docker and Docker Compose installed on your machine.
*   Python 3.x

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd ride-pricing-service
    ```

2.  **Build the Docker images:**

    ```bash
    docker-compose build
    ```

### Running Locally

1.  **Start the services using Docker Compose:**

    ```bash
    docker-compose up -d
    ```

    This command starts Redpanda, Redpanda Console, PostgreSQL, and the Pricing Service in detached mode.

2.  **Access the services:**

    *   **Pricing Service API:** `http://localhost:8000`
    *   **Redpanda Console:** `http://localhost:8080`
    *   **PostgreSQL:** `localhost:5432`

💻 **Usage**

1.  **Produce Ride Requests to Kafka:**

    The `src/producer/run.py` script simulates ride requests and sends them to the `ride_requests` Kafka topic.  You can run this script separately (outside of Docker) if you have the required Python dependencies installed, or you can create a Docker container for it.  Note that the `docker-compose.yaml` does not include a service for running the producer, so you will need to run it separately.

    ```bash
    python src/producer/run.py
    ```

2.  **Interact with the Pricing Service API:**

    *   **Health Check:**  Send a GET request to `http://localhost:8000/health` to check the service's health.
    *   **Predict Price (for testing):** Send a POST request to `http://localhost:8000/predict` with a JSON payload conforming to the `RideRequest` schema (defined in `src/pricing_service/app.py`).  Example:

        ```json
        {
          "ride_id": "test_ride",
          "distance_km": 10,
          "traffic_multiplier": 1.2
        }
        ```

        The API will return a predicted price.

📂 **Project Structure**

```
ride-pricing-service/
├── src/
│   ├── data/
│   │   └── historical_rides.csv  # Historical ride data
│   ├── data_generation/
│   │   └── generate_data.py   # Script to generate historical data
│   ├── model_training/
│   │   └── train.py           # Script to train the XGBoost model
│   ├── models/
│   │   └── xgb_pricing_model.json  # Trained XGBoost model
│   ├── pricing_service/
│   │   └── app.py             # FastAPI application for pricing service
│   ├── producer/
│   │   └── run.py             # Script to simulate ride request producer
├── docker-compose.yaml      # Docker Compose configuration file
├── README.md                # This file
```

**License**

This project is licensed under the [MIT License](LICENSE).

**Contact**

Darshil Patel - [dpatel0698@gmail.com]
