import json
import joblib
import pandas as pd
import paho.mqtt.client as mqtt

# load model and features
model = joblib.load("rf_ids_model.pkl")
feature_columns = joblib.load("feature_columns.pkl")

BROKER = "127.0.0.1"
INPUT_TOPIC = "iot/traffic"
OUTPUT_TOPIC = "iot/ids_alerts"

benign_count = 0
malicious_count = 0

def on_connect(client, userdata, flags, rc):
    print(f"Connected to broker with code {rc}")
    client.subscribe(INPUT_TOPIC)

def preprocess(sample_dict):
    df = pd.DataFrame([sample_dict])

    # Add missing features with default value 0
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0
    
    # Ensure columns are in the same order as training
    df = df[feature_columns]
    return df

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    df = preprocess(data)
    
    df.replace('-', 0, inplace=True)
    df = df.apply(pd.to_numeric, errors='coerce')
    df.fillna(0, inplace=True)
    
    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0][1]
    
    result = {
        "prediction": int(prediction),
        "probability": float(probability),
    }
    
    print(f"Prediction: {prediction}, Probability: {probability:.3f}")
    
    if probability > 0.6:
        print(f"ALERT: Suspicious traffic detected!")
    
    global benign_count, malicious_count
    
    if prediction == 0:
        benign_count += 1
    else:
        malicious_count += 1
    
    print(f"Benign: {benign_count}, Malicious: {malicious_count}")
    
    client.publish(OUTPUT_TOPIC, json.dumps(result))
    
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
print(f"Connecting to MQTT broker at {BROKER}...")

client.connect(BROKER, 1883, 60)

print("Listening for IoT traffic...")
client.loop_forever()