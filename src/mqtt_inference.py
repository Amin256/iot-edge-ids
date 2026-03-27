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
total_count = 0

correct = 0
true_positive = 0
false_positive = 0
false_negative = 0

true_benign = 0
true_malicious = 0

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
    true_label = data.pop("true_label")
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
    
    threshold_prediction = 1 if probability > 0.5 else 0
    
    global correct, true_positive, false_positive, false_negative, true_benign, true_malicious
    if true_label == 0:
        true_benign += 1
    else:
        true_malicious += 1
        
    #Accuracy tracking
    if prediction == true_label:
        correct += 1
    
    #Detection tracking
    if threshold_prediction == 1 and true_label == 1:
        true_positive += 1
    elif threshold_prediction == 1 and true_label == 0:
        false_positive += 1
    elif threshold_prediction == 0 and true_label == 1:
        false_negative += 1
    
    if probability > 0.5:
        print(f"ALERT: Suspicious traffic detected!")
    
    global benign_count, malicious_count, total_count
    total_count += 1
    
    if threshold_prediction == 0:
        benign_count += 1
    else:
        malicious_count += 1
    
    print(f"Total: {total_count}, Benign: {benign_count}, Malicious: {malicious_count}")
    accuracy = correct / total_count if total_count > 0 else 0
    detection_rate = true_positive / true_malicious if true_malicious > 0 else 0
    false_positive_rate = false_positive / true_benign if true_benign > 0 else 0
    
    print(f"Accuracy: {accuracy:.3f}")
    print(f"Detection Rate: {detection_rate:.3f}")
    print(f"False Positive Rate: {false_positive_rate:.3f}")
    
    client.publish(OUTPUT_TOPIC, json.dumps(result))
    
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
print(f"Connecting to MQTT broker at {BROKER}...")

client.connect(BROKER, 1883, 60)

print("Listening for IoT traffic...")
client.loop_forever()