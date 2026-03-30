import json
import time
import random
import pandas as pd
import paho.mqtt.client as mqtt

random.seed(42)

BROKER = "192.168.0.238"
PORT = 1883
TOPIC = "iot/traffic"

N_SAMPLES = 1000
BENIGN_RATIO = 0.99

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

df = pd.read_csv("data/iot23_processed/iot23_encoded.csv")

benign_df = df[df["binary_label"] == "BENIGN"].drop(columns=["binary_label"])
malicious_df = df[df["binary_label"] == "MALICIOUS"].drop(columns=["binary_label"])

print(f"Starting experiment: {int(BENIGN_RATIO*100)}/{int((1-BENIGN_RATIO)*100)} split")

for i in range(N_SAMPLES):
    if random.random() < BENIGN_RATIO:
        row = benign_df.sample(n=1).iloc[0]
        true_label = 0
    else:
        row = malicious_df.sample(n=1).iloc[0]
        true_label = 1
    
    sample_dict = row.to_dict()
    sample_dict["true_label"] = true_label
    
    payload = json.dumps(sample_dict)
    client.publish(TOPIC, payload)
    
    if i % 50 == 0:
        print(f"Sent {i}/{N_SAMPLES}")
    
    time.sleep(0.01)
    
print("Experiment completed!")