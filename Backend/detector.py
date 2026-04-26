CATEGORIES = {
    "sensitive": (["otp", "password", "bank"], 2.0, "Sensitive Info Request"),
    "link": (["http", "https"], 1.5, "External Link"),
    "fake_earnings": (["job", "earn", "per day", "online tasks", "₹", "$", "per day income", "no experience"], 1.5, "Unrealistic Earnings/Job"),
    "urgency": (["hurry", "limited", "now", "urgent", "immediately"], 1.0, "Urgency"),
    "action": (["click", "register", "verify", "confirm", "login"], 1.0, "Action Request"),
    "off_platform": (["whatsapp", "telegram"], 1.0, "Off-Platform Shift"),
    "reward": (["won", "congratulations", "prize"], 0.5, "Reward/Prize")
}

def rule_based_score(text):
    text_lower = text.lower()
    score = 0.0
    detected = []
    risk_factors = []

    for cat_name, (words, weight, label) in CATEGORIES.items():
        if any(w in text_lower for w in words):
            score += weight
            detected.append(cat_name)
            risk_factors.append(label)

    attack_type = "None"
    
    if "fake_earnings" in detected:
        attack_type = "Job Scam"
    elif "reward" in detected:
        attack_type = "Lottery Scam"
    elif "sensitive" in detected and "bank" in text_lower:
        attack_type = "Banking Fraud"
    elif "sensitive" in detected or "action" in detected:
        attack_type = "Phishing"
    elif score > 0:
        attack_type = "Suspicious Message"

    if score >= 3:
        risk = "Dangerous"
    elif score >= 1.5:
        risk = "Suspicious"
    else:
        risk = "Safe"

    explanation = f"This message shows signs of {attack_type}." if score > 0 else "No active threat patterns detected."
    
    actions = []
    if attack_type == "Job Scam":
        actions = ["Do not message unknown numbers on WhatsApp/Telegram.", "Do not pay any money for a job setup."]
    elif attack_type == "Lottery Scam":
        actions = ["Ignore the message.", "Do not pay any processing fees."]
    elif attack_type == "Banking Fraud":
        actions = ["Contact your bank directly.", "Never share your OTP."]
    elif attack_type == "Phishing":
        actions = ["Do not enter your password.", "Verify the sender's identity."]
    elif score > 0:
        actions = ["Do not interact with the message."]
    else:
        actions = ["Message appears safe, but stay vigilant."]

    return score, risk, attack_type, risk_factors, explanation, actions