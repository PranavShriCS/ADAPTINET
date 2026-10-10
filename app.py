
from pathlib import Path
import json
import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"

MODEL_FILE = MODEL_DIR / "congestion_model.joblib"
SCALER_FILE = MODEL_DIR / "congestion_scaler.joblib"
INFO_FILE = MODEL_DIR / "model_info.json"

FEATURE_COLUMNS = [
    "utilization_percent",
    "latency_ms",
    "packet_loss_percent",
    "throughput_mbps",
    "queue_occupancy_percent",
    "packet_arrival_rate_pps"
]

if not MODEL_FILE.exists() or not SCALER_FILE.exists():
    raise FileNotFoundError(
        "Trained model not found. Run train_model.py first."
    )

final_model = joblib.load(MODEL_FILE)
final_scaler = joblib.load(SCALER_FILE)


def predict_congestion(link_data):
    link_df = pd.DataFrame([link_data])
    link_features = link_df[FEATURE_COLUMNS]

    link_scaled = final_scaler.transform(link_features)

    probability = float(
        final_model.predict_proba(link_scaled)[0][1]
    )

    prediction = int(probability >= 0.5)

    return prediction, probability


def get_congestion_level(probability):
    if probability < 0.50:
        return "Nil"
    elif probability < 0.80:
        return "Moderate"
    else:
        return "High"


if __name__ == "__main__":
    sample_link = {
        "utilization_percent": 90,
        "latency_ms": 80,
        "packet_loss_percent": 5,
        "throughput_mbps": 50,
        "queue_occupancy_percent": 85,
        "packet_arrival_rate_pps": 900
    }

    prediction, probability = predict_congestion(sample_link)

    print("\n========== CONGESTION PREDICTION ==========")
    print("Predicted congestion:", prediction)
    print("Probability:", f"{probability * 100:.2f}%")
    print("Congestion level:", get_congestion_level(probability))

    if INFO_FILE.exists():
        with open(INFO_FILE, "r", encoding="utf-8") as file:
            info = json.load(file)

        print("Selected model:", info["selected_model"])
        print("Test accuracy:", info["test_accuracy"])
