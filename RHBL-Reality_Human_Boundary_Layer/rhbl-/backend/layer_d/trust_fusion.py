import numpy as np

def fuse_layers(layers_output):
    """
    layers_output = [
      {
        "layer": "human",
        "score": float,
        "confidence_interval": [low, high],
        "quality": float,
        "violated_rules": []
      },
      ...
    ]
    """

    weighted_score = 0.0
    total_weight = 0.0
    reasons = []

    for layer in layers_output:
        score = layer["score"]
        quality = layer.get("quality", 1.0)

        ci_low, ci_high = layer["confidence_interval"]
        uncertainty = ci_high - ci_low

        # weight reduces if uncertainty is high
        weight = max(0, quality * (1 - uncertainty))

        weighted_score += score * weight
        total_weight += weight

        if layer["violated_rules"]:
            reasons.append({
                "layer": layer["layer"],
                "rules": layer["violated_rules"]
            })

    if total_weight == 0:
        return {
            "trust_score": 0,
            "confidence": 0,
            "decision": "REFUSE",
            "reason": "Insufficient signal quality"
        }

    trust_score = weighted_score / total_weight
    confidence = min(1.0, total_weight / len(layers_output))

    decision = "ALLOW" if trust_score >= 0.7 else "FLAG"

    return {
        "trust_score": round(trust_score * 100, 2),
        "confidence": round(confidence, 2),
        "decision": decision,
        "reasoning_trace": reasons
    }
