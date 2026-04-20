import requests
import random
import joblib
import time

API_URL = "http://127.0.0.1:5000/predict"

print("Loading feature list...")

features = joblib.load("C:\\GenAI project\\models\\features.pkl")

print("Simulator using", len(features), "features")



def generate_base_packet():
    packet = {}

    for f in features:
        packet[f] = random.uniform(1, 500)

    return packet




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



def generate_traffic():

    scenario = random.choices(
        ["NORMAL", "DDOS", "PORT_SCAN", "BOT"],
        weights=[60, 15, 15, 10]   # more realistic distribution
    )[0]

    if scenario == "NORMAL":
        packet = simulate_normal()
    elif scenario == "DDOS":
        packet = simulate_ddos()
    elif scenario == "PORT_SCAN":
        packet = simulate_port_scan()
    else:
        packet = simulate_bot()

    return scenario, packet



print("Starting traffic simulation...")

packet_count = 0

while True:

    scenario, packet = generate_traffic()
    packet_count += 1

    try:

        response = requests.post(
            API_URL,
            json=packet,
            timeout=3   # 🔥 prevents freezing
        )

        if response.status_code != 200:
            print("API error:", response.text)
            time.sleep(2)
            continue

        result = response.json()

        print("\n------------------------------")
        print(f"Packet: {packet_count}")
        print("Simulated Traffic:", scenario)
        print("Prediction:", result.get("prediction"))
        print("Risk Score:", round(result.get("risk_score", 0), 2))

        if result.get("prediction") == "ATTACK":
            print("🚨 ATTACK DETECTED:", result.get("threat_type"))

        # 🔥 Control speed (VERY IMPORTANT)
        time.sleep(random.uniform(0.8, 1.5))

    except requests.exceptions.Timeout:
        print("⚠️ API timeout... retrying")
        time.sleep(2)

    except requests.exceptions.ConnectionError:
        print("❌ API server not running")
        time.sleep(3)

    except Exception as e:
        print("Unexpected error:", str(e))
        time.sleep(2)