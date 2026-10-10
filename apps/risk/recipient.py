def evaluate_recipient(recipient):
    signals = []
    if recipient.get("is_new"):
        signals.append({"code": "NEW_RECIPIENT", "score": 35, "severity": "MEDIUM", "confidence": 0.92,
                        "description": "Recipient has not appeared in the sender's known history"})
    verification = str(recipient.get("verification_level", "")).upper()
    if verification in {"LOW", "UNVERIFIED"}:
        signals.append({"code": "LOW_RECIPIENT_VERIFICATION", "score": 30, "severity": "MEDIUM", "confidence": 0.9,
                        "description": "Recipient verification level is low or unavailable"})
    if recipient.get("account_age_days") is not None and recipient["account_age_days"] < 30:
        signals.append({"code": "NEW_RECIPIENT_ACCOUNT", "score": 25, "severity": "MEDIUM", "confidence": 0.88,
                        "description": "Recipient account is recently created"})
    if recipient.get("historical_risk") in {"HIGH", "CRITICAL"}:
        signals.append({"code": "RECIPIENT_RISK_HISTORY", "score": 70, "severity": "HIGH", "confidence": 0.95,
                        "description": "Recipient has a high historical risk indicator"})
    return min(100, sum(signal["score"] for signal in signals)), signals


def demo_recipient_context(recipient_token):
    """Synthetic demo enrichment; replace with authorized recipient intelligence in production."""
    token = recipient_token.lower()
    return {
        "is_new": token.startswith("rcp_new"),
        "verification_level": "LOW" if "low" in token or token.startswith("rcp_new") else "HIGH",
        "account_age_days": 14 if token.startswith("rcp_new") else 900,
        "historical_risk": "HIGH" if "reported" in token else "LOW",
    }
