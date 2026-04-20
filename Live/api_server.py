from flask import Flask, request, jsonify
import joblib
import pandas as pd
from report_generator import generate_report, create_pdf
from risk_engine import calculate_risk_score
from incident_store import log_incident

app = Flask(__name__)

print("Loading ML components...")

model = joblib.load("C:\\GenAI project\\models\\intrusion_model.pkl")
scaler = joblib.load("C:\\GenAI project\\models\\scaler.pkl")
features = joblib.load("C:\\GenAI project\\models\\features.pkl")

print("Model expects", len(features), "features")


total_packets = 0
attacks = 0
normal = 0
last_report = "No incidents yet"

def classify_threat(packet):

    if packet.get("Packet Length Variance", 0) > 800:
        return "Possible DDoS Traffic"

    if packet.get("Packet Length Std", 0) > 300:
        return "Port Scanning Activity"

    if packet.get("Average Packet Size", 0) < 100:
        return "Suspicious Bot Activity"

    return "Unknown Suspicious Pattern"



@app.route("/predict", methods=["POST"])
def predict():

    global total_packets, attacks, normal, last_report

    try:

        data = request.json

       
        input_data = {}

        for f in features:
            input_data[f] = data.get(f, 0)

        df = pd.DataFrame([input_data])

        # Scale input
        scaled = scaler.transform(df)

        # ------------------------------------------------
        # ML Prediction
        # ------------------------------------------------

        prediction = model.predict(scaled)[0]
        probability = model.predict_proba(scaled)[0][1]

        # ------------------------------------------------
        # Rule-based detection
        # ------------------------------------------------

        rule_attack = False

        if data.get("Packet Length Variance", 0) > 800:
            rule_attack = True

        if data.get("Packet Length Std", 0) > 300:
            rule_attack = True

        if data.get("Average Packet Size", 0) < 120:
            rule_attack = True

        # Final decision
        if prediction == 1 or rule_attack:
            prediction = 1

        total_packets += 1

        # ------------------------------------------------
        # ATTACK DETECTED
        # ------------------------------------------------

        if prediction == 1:

            attacks += 1

            threat_type = classify_threat(data)

            # Risk Score
            risk_score = calculate_risk_score("ATTACK", probability)

            # Log Incident
            incident = log_incident(data, "ATTACK", risk_score)

            # Generate AI Report
            last_report = generate_report(incident, threat_type)

            # Generate PDF Report
            pdf_file = create_pdf(last_report)

            return jsonify({
                "prediction": "ATTACK",
                "threat_type": threat_type,
                "risk_score": risk_score,
                "report": last_report,
                "pdf_report": pdf_file
            })

        # ------------------------------------------------
        # NORMAL TRAFFIC
        # ------------------------------------------------

        else:

            normal += 1

            risk_score = calculate_risk_score("NORMAL", probability)

            return jsonify({
                "prediction": "NORMAL",
                "risk_score": risk_score
            })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500




@app.route("/stats")
def stats():

    return jsonify({
        "total_packets": total_packets,
        "attacks": attacks,
        "normal": normal,
        "last_report": last_report
    })


if __name__ == "__main__":
    print("Starting AI Intrusion Detection API...")
    app.run(host="127.0.0.1", port=5000, debug=True)