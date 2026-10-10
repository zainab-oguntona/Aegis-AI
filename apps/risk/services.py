from decimal import Decimal


MODULE_WEIGHTS = {"facial": Decimal("0.20"), "behavioral": Decimal("0.45"), "environment": Decimal("0.35")}


def fuse_scores(module_scores, enabled_modules):
    selected = [module for module in enabled_modules if module in MODULE_WEIGHTS and module in module_scores]
    if not selected:
        return 0
    weight_total = sum((MODULE_WEIGHTS[module] for module in selected), Decimal("0"))
    score = sum((Decimal(str(module_scores[module])) * MODULE_WEIGHTS[module] for module in selected), Decimal("0"))
    return max(0, min(100, round(score / weight_total)))


def classify_score(score, policy=None):
    policy = policy or {}
    thresholds = {"monitor": policy.get("monitor", 20), "step_up": policy.get("step_up", 50),
                  "hold": policy.get("hold", 70), "critical": policy.get("critical", 86)}
    if score <= thresholds["monitor"]:
        return "LOW", "ALLOW"
    if score <= thresholds["step_up"]:
        return "MEDIUM", "MONITOR"
    if score < thresholds["hold"]:
        return "HIGH", "STEP_UP"
    if score < thresholds["critical"]:
        return "HIGH", "HOLD"
    return "CRITICAL", "HOLD"


def explain_assessment(module_scores, decision):
    explanations = []
    labels = {"facial": "facial distress", "behavioral": "transaction behavior", "environment": "device and environment"}
    for module, score in module_scores.items():
        if score >= 70:
            explanations.append(f"high {labels.get(module, module)} risk ({score}/100)")
        elif score >= 40:
            explanations.append(f"elevated {labels.get(module, module)} risk ({score}/100)")
    if not explanations:
        explanations.append("no material anomaly detected")
    status = "SUCCESSFUL" if decision == "ALLOW" else "PENDING" if decision in {"MONITOR", "STEP_UP"} else "STOPPED"
    return status, explanations
