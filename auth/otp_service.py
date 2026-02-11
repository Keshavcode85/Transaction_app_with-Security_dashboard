import random
import time

# In-memory OTP store (for demo)
_otp_store = {}


def generate_otp(user_id, expiry_seconds=300):
    otp = str(random.randint(100000, 999999))
    _otp_store[user_id] = {
        "otp": otp,
        "expires_at": time.time() + expiry_seconds
    }
    return otp


def verify_otp(user_id, otp):
    record = _otp_store.get(user_id)

    if not record:
        return False

    if time.time() > record["expires_at"]:
        _otp_store.pop(user_id, None)
        return False

    if record["otp"] != otp:
        return False

    _otp_store.pop(user_id, None)
    return True
