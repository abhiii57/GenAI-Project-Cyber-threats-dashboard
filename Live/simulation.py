import requests
import random
import time
import joblib

API_URL = "http://127.0.0.1:5000/predict"

print("Loading feature list...")

features = joblib.load("C:\\GenAI project\\models\\features.pkl")

print("Simulator using", len(features), "features")

# ------------------------------------------------
# Feature Generator
# ------------------------------------------------

def generate_base_packet():

    packet = {}

    for f in features:

        # Default random traffic
        packet[f] = random.uniform(1, 500)

    return packet


# ------------------------------------------------
# Traffic Profiles
# ------------------------------------------------

def simulate_normal():

    packet = generate_base_packet()

    packet["Average Packet Size"] = random.uniform(400, 900)
    packet["Packet Length Std"] = random.uniform(10, 80)
    packet["Packet Length Variance"] = random.uniform(50, 200)

    return packet


def simulate_ddos():

    packet = generate_base_packet()

    packet["Average Packet Size"] = random.uniform(100, 200)
    packet["Packet Length Std"] = random.uniform(200, 400)
    packet["Packet Length Variance"] = random.uniform(800, 1200)

    return packet


def simulate_port_scan():

    packet = generate_base_packet()

    packet["Destination Port"] = random.randint(1, 65535)
    packet["Packet Length Std"] = random.uniform(300, 500)
    packet["Packet Length Variance"] = random.uniform(400, 700)

    return packet


def simulate_bot():

    packet = generate_base_packet()

    packet["Average Packet Size"] = random.uniform(20, 80)
    packet["Packet Length Std"] = random.uniform(100, 200)

    return packet


# ------------------------------------------------
# Scenario Selector
# ------------------------------------------------

def generate_traffic():

    scenario = random.choice([
        "NORMAL",
        "DDOS",
        "PORT_SCAN",
        "BOT"
    ])

    if scenario == "NORMAL":
        packet = simulate_normal()

    elif scenario == "DDOS":
        packet = simulate_ddos()

    elif scenario == "PORT_SCAN":
        packet = simulate_port_scan()

    else:
        packet = simulate_bot()

    return scenario, packet


# ------------------------------------------------
# Simulation Loop
# ------------------------------------------------

print("Starting traffic simulation...")

while True:

    scenario, packet = generate_traffic()

    try:

        response = requests.post(API_URL, json=packet)

        if response.status_code == 200:

            result = response.json()

            print("\n------------------------------")
            print("Simulated Traffic:", scenario)
            print("Prediction:", result["prediction"])

            if result["prediction"] == "ATTACK":
                print("Threat Type:", result.get("threat_type"))
                print("Risk Score:", result.get("risk_score"))

        else:

            print("API error:", response.text)

    except:

        print("API server not running")

    time.sleep(1)