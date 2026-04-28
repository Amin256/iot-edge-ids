# IoT Edge Intrusion Detection System

Final Year Project - University of Leeds

This project implements and evaluates a machine-learning-based intrusion detection system (IDS) for IoT and edge environments.

The focus is on deploying supervised ML models on resource-constrained devices (e.g. Raspberry Pi) and evaluating performance using benchmark IoT datasets such as IoT-23.

## Key Features
- Real-time intrusion detection on Raspberry Pi
- MQTT-based data transmission pipeline
- Flow-based feature extraction from network traffic
- Evaluation under realistic conditions:
  - Random split
  - Capture-based validation
  - Class imbalance (95/5 and 99/1)
- Deployment metrics:
  - Detection rate
  - False positive rate
  - Precision, recall, F1-score
  - Inference latency

## Key Technologies Used
- Python
- XGBoost
- Scikit-learn
- Pandas / NumPy
- MQTT (paho-mqtt)
- Raspberry Pi 5

## Repository structure
- notebooks/ --> Model training and evaluation notebook
- src/ --> Core pipeline scripts
- models/ --> Trained ML models
- data/ --> Processed datasets (subsets only)

## Key Files
- `notebooks/baseline_model.ipynb` --> Main notebook containing model training, evaluation and comparison experiments
- `src/mqtt_inference.py` --> Real-time inference module used on the Raspberry Pi
- `src/mqtt_sender.py` --> Sends test traffic samples to the MQTT broker
- `src/iot23_parser.py` --> Parses IoT-23 labelled logs into structured features

## How to run
### 1. Install dependencies
pip install -r requirements.txt
### 2. Run MQTT inference (on Raspberry Pi
python src/mqtt_inference.py
### 3. Run sender (on external machine)
python src/mqtt_sender.py

## Notes
- Full datasets are not included due to size constraints
- The repository contains a processed subset used for testing and demonstration
- This project accompanies a final year dissertation on edge-based IDS systems

## Author
Amin Bichbich
