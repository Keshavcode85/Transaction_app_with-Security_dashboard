from datetime import datetime, timedelta
from flask import current_app
from database.models import LoginAttempt


def calculate_risk(ip_address, user_agent, recent_attempts):
    """
    Simple risk scoring logic
    """

    risk_score = 0

    # Rule 1: Too many failed attempts
    failed_attempts = [a for a in recent_attempts if not a.success]
    if len(failed_attempts) >= current_app.config["MAX_LOGIN_ATTEMPTS"]:
        risk_score += 40

    # Rule 2: New / suspicious user agent
    agents = set(a.user_agent for a in recent_attempts)
    if user_agent not in agents and agents:
        risk_score += 20

    # Rule 3: New IP address
    ips = set(a.ip_address for a in recent_attempts)
    if ip_address not in ips and ips:
        risk_score += 20

    return risk_score
