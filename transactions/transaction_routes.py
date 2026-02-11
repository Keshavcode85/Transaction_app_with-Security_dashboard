from flask import Blueprint, request, jsonify
from database.db import db
from database.models import Transaction
from transactions.transaction_checker import is_transaction_suspicious

transaction_bp = Blueprint("transactions", __name__)


@transaction_bp.route("/transfer", methods=["POST"])
def transfer_money():
    data = request.get_json()

    sender_id = data.get("sender_id")
    receiver_id = data.get("receiver_id")
    amount = data.get("amount")

    if not sender_id or not receiver_id or not amount:
        return jsonify({"message": "Missing required fields"}), 400

    # Check for suspicious transaction
    if is_transaction_suspicious(sender_id, amount):
        return jsonify({
            "status": "blocked",
            "message": "Suspicious transaction detected"
        }), 403

    transaction = Transaction(
        sender_id=sender_id,
        receiver_id=receiver_id,
        amount=amount,
        status="SUCCESS"
    )

    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Transaction completed"
    }), 200
