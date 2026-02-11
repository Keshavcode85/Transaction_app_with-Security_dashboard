from database.models import Transaction


def is_transaction_suspicious(sender_id, amount):
    """
    Simple rule-based transaction check
    Can be replaced by ML model later
    """

    # Rule 1: Very high amount
    if amount > 100000:
        return True

    # Rule 2: Too many transactions by sender
    recent_count = Transaction.query.filter_by(sender_id=sender_id).count()
    if recent_count > 20:
        return True

    return False
