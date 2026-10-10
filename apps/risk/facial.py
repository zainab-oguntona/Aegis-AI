from decimal import Decimal


def evaluate_facial(ml_result, identity_verified=None):
    distress = sum(Decimal(str(ml_result.get(emotion, 0))) for emotion in ("fear", "sad", "angry"))
    confidence = max(Decimal("0"), min(Decimal("1"), sum(Decimal(str(value)) for value in ml_result.values())))
    score = min(100, round(float(distress * 100)))
    signals = []
    if distress >= Decimal("0.45"):
        signals.append({"code": "FACIAL_DISTRESS_SIGNAL", "score": score, "severity": "HIGH" if score >= 70 else "MEDIUM",
                        "confidence": float(confidence), "description": "Elevated distress-related facial signal"})
    if identity_verified is False:
        signals.append({"code": "IDENTITY_NOT_VERIFIED", "score": 20, "severity": "MEDIUM", "confidence": 1.0,
                        "description": "The fintech supplied an unsuccessful identity-verification result"})
        score = min(100, score + 20)
    return score, float(confidence), signals
