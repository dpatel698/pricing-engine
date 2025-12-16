import time
import json
import logging
import threading
from contextlib import asynccontextmanager
import pandas as pd
from kafka import KafkaConsumer
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import xgboost as xgb

# Define Model Path
MODEL_PATH = 'models/xgb_pricing_model.json'

# Global variable to hold the loaded model
MODEL: xgb.Booster = None

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- In-Memory State/Feature Store ---
# In production, this would be Redis/Feast
# We will store the latest predicted price for each ride_id.
LATEST_PRICES: Dict[str, Any] = {}


# --- Pydantic Schema for API Input (just for testing/health) ---
class RideRequest(BaseModel):
    ride_id: str
    distance_km: float
    traffic_multiplier: float


# --- Core Consumer Class (Runs in a separate thread) ---
class PricingConsumer(threading.Thread):
    def __init__(self, broker: str, topic: str, group_id: str):
        super().__init__()
        self.stop_event = threading.Event()
        self.broker = broker
        self.topic = topic
        self.group_id = group_id

    def calculate_price_dummy(self, data: dict) -> float:
        """
        [THE DUMB MODEL]
        A simple rule-based system used to test the initial setup.
        """
        BASE_RATE_PER_KM = 2.50

        # Calculate base price, then apply time-based traffic multiplier
        price = data['distance_km'] * BASE_RATE_PER_KM * data['traffic_multiplier']
        return round(price, 2)

    # Inside the PricingConsumer class:
    def calculate_price(self, data: dict) -> float:
        """
        [THE XGBOOST MODEL PREDICTION]
        Uses the loaded XGBoost model for prediction.
        """
        global MODEL
        if MODEL is None:
            # This fallback is now only hit if loading failed at startup
            return 10.0


        # 1. Define the features based on the Producer's data
        feature_data = {
            'distance_km': [data['distance_km']],
            'traffic_multiplier': [data['traffic_multiplier']],
            # The Producer doesn't send this yet, so we use a dummy value (0.0)
            'time_of_day_sin': [0.0]
        }

        # 2. Convert to Pandas DataFrame (Crucial for passing feature names)
        # The columns MUST be in the same order as in train.py
        input_df = pd.DataFrame(feature_data)

        # 3. Predict: Wrap the DataFrame in a DMatrix
        dmatrix = xgb.DMatrix(input_df)

        # 4. Get prediction
        predicted_price = MODEL.predict(dmatrix)[0]

        return round(float(predicted_price), 2)

    def run(self):
        try:
            consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=[self.broker],
                auto_offset_reset='latest',  # Only read new messages
                enable_auto_commit=True,
                group_id=self.group_id,
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            logger.info(f"Consumer started for topic: {self.topic}")

            for message in consumer:
                if self.stop_event.is_set():
                    break

                ride_data = message.value

                # 1. Calculate the price
                predicted_price = self.calculate_price(ride_data)

                # 2. Store the result in our in-memory store
                ride_id = ride_data.get('ride_id')
                LATEST_PRICES[ride_id] = {
                    "price": predicted_price,
                    "timestamp": time.time()
                }

                logger.info(f"Processed Ride {ride_id[:8]} | Price: ${predicted_price}")

        except Exception as e:
            logger.error(f"Consumer Error: {e}")
        finally:
            if 'consumer' in locals():
                consumer.close()
            logger.info("Consumer stopped.")

    def stop(self):
        self.stop_event.set()


# --- FastAPI Lifespan (Startup/Shutdown) ---
consumer_thread: PricingConsumer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    global consumer_thread, MODEL
    logger.info("Loading XGBoost Model...")
    try:
        # CHANGE: Load the native Booster from the JSON file
        MODEL = xgb.Booster(model_file=MODEL_PATH)
        logger.info("✅ XGBoost Model loaded successfully.")
    except Exception as e:
        logger.error(f"❌ Error loading model at {MODEL_PATH}. Check file path. Error: {e}")

    # NOTE: We use 'redpanda:9092' because this app will run INSIDE Docker
    consumer_thread = PricingConsumer(
        broker='redpanda:9092',
        topic='ride_requests',
        group_id='pricing_service_group'
    )
    consumer_thread.start()
    logger.info("FastAPI App and Consumer starting up...")
    yield

    # SHUTDOWN
    if consumer_thread:
        consumer_thread.stop()
        consumer_thread.join()
    logger.info("FastAPI App shutting down...")


app = FastAPI(lifespan=lifespan, title="Real-Time Pricing Service")


# --- API Endpoints ---
@app.get("/")
def health_check():
    return {"status": "OK", "consumer_status": "Running"}


@app.get("/price/{ride_id}")
def get_latest_price(ride_id: str):
    """
    Endpoint to retrieve the price that was calculated by the consumer thread.
    """
    price_info = LATEST_PRICES.get(ride_id)
    if not price_info:
        raise HTTPException(status_code=404, detail="Ride ID not found or not yet processed.")

    return {
        "ride_id": ride_id,
        "price": price_info['price'],
        "timestamp_utc": price_info['timestamp']
    }
