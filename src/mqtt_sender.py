import json
import time
import random
import pandas as pd
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "iot/traffic"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

df = pd.read_csv("data/iot23_processed/iot23_encoded.csv")

benign_df = df[df["binary_label"] == "BENIGN"]
malicious_df = df[df["binary_label"] == "MALICIOUS"]

benign_df = benign_df.drop(columns=["binary_label"])
malicious_df = malicious_df.drop(columns=["binary_label"])

print("Starting real data stream...")

while True:
    if random.random() < 0.95:
        row = benign_df.sample(1).iloc[0]
        true_label = 0
    else:
        row = malicious_df.sample(1).iloc[0]
        true_label = 1

    sample_dict = row.to_dict()
    sample_dict["true_label"] = true_label
    payload = json.dumps(sample_dict)
    client.publish(TOPIC, payload)
    print(f"Sent: {payload}")
    time.sleep(0.05)