from datetime import datetime

incidents = []

def log_incident(packet, prediction, score):

    event = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prediction": prediction,
        "risk_score": score,
        "packet": packet
    }

    incidents.append(event)

    return event


def get_incidents():
    return incidents