import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import root_mean_squared_error
import os

# Define paths relative to the script location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'src', 'data', 'historical_rides.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'src', 'models', 'xgb_pricing_model.json')


def train_and_save_model():
    print("⏳ Starting model training (using native Booster)...")

    # 1. Load Data
    try:
        df = pd.read_csv(DATA_PATH)
    except FileNotFoundError:
        print(f"❌ Data file not found at {DATA_PATH}. Run generate_data.py first.")
        return

    # 2. Define Features (X) and Target (y)
    features = ['distance_km', 'traffic_multiplier', 'time_of_day_sin']
    target = 'final_price'

    X = df[features]
    y = df[target]

    # 3. Split Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)

    # 4. Define Parameters and Train Model (using native xgb.train)
    params = {
        'objective': 'reg:squarederror',
        'eta': 0.1,  # learning_rate equivalent
        'max_depth': 6,
        'seed': 42
    }

    # Train the native Booster
    bst = xgb.train(
        params,
        dtrain,
        num_boost_round=100
    )

    # 5. Evaluate Model
    y_pred = bst.predict(dtest)
    rmse = root_mean_squared_error(y_test, y_pred)
    print(f"✅ Training Complete. RMSE on test set: ${rmse:.2f}")

    # 6. Save Model Artifact (using the native Booster's save_model)
    bst.save_model(MODEL_PATH)
    print(f"💾 Model saved to: {MODEL_PATH}")


if __name__ == '__main__':
    train_and_save_model()