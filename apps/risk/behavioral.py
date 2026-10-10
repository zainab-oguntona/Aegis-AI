from decimal import Decimal


def evaluate_behavior(amount, recipient, sender_profile):
    signals = []
    average = Decimal(str(sender_profile.get("average_transaction_amount", 0)))
    maximum = Decimal(str(sender_profile.get("maximum_transaction_amount", 0)))

    if maximum and amount > maximum:
        score = min(100, round(float((amount / maximum) * 45)))
        signals.append({"code": "AMOUNT_ANOMALY", "score": max(40, score), "severity": "HIGH", "confidence": 0.95,
                        "description": "Amount exceeds the sender's historical maximum"})
    elif average and amount > average * 3:
        signals.append({"code": "AMOUNT_DEVIATION", "score": 35, "severity": "MEDIUM", "confidence": 0.9,
                        "description": "Amount is materially above the sender's historical average"})

    if recipient.get("is_new"):
        signals.append({"code": "NEW_RECIPIENT", "score": 35, "severity": "MEDIUM", "confidence": 0.92,
                        "description": "Recipient has not appeared in the sender's known history"})
    if str(recipient.get("verification_level", "")).upper() in {"LOW", "UNVERIFIED"}:
        signals.append({"code": "LOW_RECIPIENT_VERIFICATION", "score": 30, "severity": "MEDIUM", "confidence": 0.9,
                        "description": "Recipient verification level is low or unavailable"})

    score = min(100, sum(signal["score"] for signal in signals))
    return score, signals
