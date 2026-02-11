from flask import Flask, render_template, redirect, url_for, session, request
from config import Config
from database.db import init_db, db
from auth.auth_routes import auth_bp
from transactions.transaction_routes import transaction_bp
from security.login_checker import security_bp
from database.models import User
import requests


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ---------------- INIT DB ----------------
    init_db(app)

    # ---------------- REGISTER BLUEPRINTS ----------------
    app.register_blueprint(auth_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(security_bp)

    # ---------------- CREATE DEFAULT ADMIN ----------------
    with app.app_context():
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@gmail.com"
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()

    # ================= NORMAL DASHBOARD =================
    @app.route("/dashboard")
    def dashboard():
        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        return render_template("dashboard.html")

    # ================= SUSPICIOUS DASHBOARD =================
    @app.route("/suspicious_dashboard", methods=["GET", "POST"])
    def suspicious_dashboard():

        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        result = None
        hidden_data = None
        role = "admin"   # agar role session me hai toh session["role"] use kar sakte ho

        if request.method == "POST":
            try:
                # ML Service Call
                ml_response = requests.post(
                    "http://192.168.1.7:6000/predict-login",  # ML app ka correct endpoint
                    json={
                        "attempts": 3,
                        "status": "success"
                    },
                    timeout=5
                ).json()

                decision = ml_response.get("decision")

                # Template ke hisaab se result structure
                result = {
                    "total": 1,
                    "suspicious": 1 if decision != "ALLOW" else 0,
                    "normal": 1 if decision == "ALLOW" else 0
                }

            except Exception as e:
                result = {
                    "total": 0,
                    "suspicious": 0,
                    "normal": 0
                }

        return render_template(
            "suspicious_dashboard.html",
            result=result,
            hidden_data=hidden_data,
            role=role
        )

    # ================= HANDLE ALERT =================
    @app.route("/handle-alert", methods=["POST"])
    def handle_alert():

        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        choice = request.form.get("choice")

        if choice == "yes":
            return redirect(url_for("suspicious_dashboard"))
        else:
            return redirect(url_for("dashboard"))

    # ================= HOME =================
    @app.route("/")
    def home():
        return redirect(url_for("auth.login"))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True,port=5000)
