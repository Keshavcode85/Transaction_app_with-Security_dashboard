def send_alert(user_id, risk_score):
    """
    Send alert to user/admin
    (Email / SMS can be added later)
    """

    print("⚠️ ALERT ⚠️")
    print(f"User ID: {user_id}")
    print(f"High Risk Score: {risk_score}")
    print("Suspicious login detected!")
