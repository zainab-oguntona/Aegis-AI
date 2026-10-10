def evaluate_environment(device, network, location, telecom, account_security):
    signals = []
    checks = [
        (device.get("is_new"), "NEW_DEVICE", 35, "Transaction originated from a previously unseen device"),
        (network.get("new_ip"), "NEW_IP", 25, "Transaction originated from a new IP address"),
        (location.get("is_new"), "NEW_LOCATION", 30, "Transaction originated from a new location"),
        (telecom.get("recent_sim_swap"), "RECENT_SIM_SWAP", 50, "A recent SIM change was supplied by an authorized source"),
        (account_security.get("new_beneficiary"), "NEW_BENEFICIARY", 30, "A new beneficiary was recently added"),
        (account_security.get("recent_password_reset"), "RECENT_PASSWORD_RESET", 25, "A password reset recently preceded the transaction"),
        (account_security.get("recent_pin_change"), "RECENT_PIN_CHANGE", 25, "A PIN change recently preceded the transaction"),
    ]
    for active, code, score, description in checks:
        if active:
            signals.append({"code": code, "score": score, "severity": "HIGH" if score >= 40 else "MEDIUM",
                            "confidence": 0.9, "description": description})
    for category, values in (("network", network), ("location", location)):
        if str(values.get(f"{category}_risk", "")).upper() in {"HIGH", "CRITICAL"}:
            signals.append({"code": f"HIGH_{category.upper()}_RISK", "score": 45, "severity": "HIGH",
                            "confidence": 0.88, "description": f"Authorized source supplied high {category} risk"})
    return min(100, sum(signal["score"] for signal in signals)), signals
