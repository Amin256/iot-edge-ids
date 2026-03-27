import joblib
import pandas as pd

# Load model and features
model = joblib.load("rf_ids_model.pkl")
feature_columns = joblib.load("feature_columns.pkl")

def predict(sample_dict):
    df = pd.DataFrame([sample_dict])

    # Add missing features with default value 0
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0
    
    # Ensure columns are in the same order as training
    df = df[feature_columns]

    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0][1]

    return prediction, probability


if __name__ == "__main__":
    # Example test sample
    sample = {
        'duration': 1.2,
        'orig_bytes': 300,
        'resp_bytes': 1200,
        'orig_pkts': 5,
        'resp_pkts': 10
    }

    pred, prob = predict(sample)

    print(f"Prediction: {pred}")
    print(f"Probability: {prob}")