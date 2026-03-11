def calculate_risk_score(prediction, probability):

    base_score = probability * 100

    if prediction == "ATTACK":
        risk_score = min(base_score + 20, 100)
    else:
        risk_score = base_score * 0.4

    return round(risk_score,2)