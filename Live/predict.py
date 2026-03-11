import pandas as pd
import joblib

model = joblib.load("models/intrusion_model.pkl")
scaler = joblib.load("models/scaler.pkl")
features = joblib.load("models/features.pkl")


def predict_intrusion(packet):

    df = pd.DataFrame([packet])

    # add missing features automatically
    for feature in features:
        if feature not in df.columns:
            df[feature] = 0

    df = df[features]

    scaled = scaler.transform(df)

    prob = model.predict_proba(scaled)[0][1]

    prediction = "ATTACK" if prob > 0.5 else "NORMAL"

    return prediction, prob