import pandas as pd
import numpy as np
import os


def generate_historical_data(num_samples=10000):
    """Generates a synthetic historical dataset for ride pricing."""

    # Features (Inputs)
    distance_km = np.random.uniform(1, 30, num_samples)
    traffic_multiplier = np.random.uniform(1.0, 3.0, num_samples)
    time_of_day_sin = np.random.uniform(-1, 1, num_samples)  # Cyclic feature example

    # Target (Output - The Price)
    # Price = (Distance * $3.50) + (Traffic Multiplier * $5) + (Time-of-Day factor) + noise
    base_price = (distance_km * 3.50)
    traffic_premium = (traffic_multiplier - 1) * 5.0  # Premium for high traffic

    # Add a slight premium for peak hours (based on sine wave)
    time_premium = time_of_day_sin * 1.5

    noise = np.random.normal(0, 5.0, num_samples)  # Random fluctuation

    final_price = base_price + traffic_premium + time_premium + noise
    # Ensure all prices are positive
    final_price[final_price < 5.0] = 5.0

    data = pd.DataFrame({
        'distance_km': distance_km,
        'traffic_multiplier': traffic_multiplier,
        'time_of_day_sin': time_of_day_sin,
        'final_price': final_price
    })

    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'historical_rides.csv')
    data.to_csv(output_path, index=False)
    print(f"✅ Generated dataset saved to: {output_path}")


if __name__ == '__main__':
    # Make sure the 'data' directory exists
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'), exist_ok=True)
    generate_historical_data()