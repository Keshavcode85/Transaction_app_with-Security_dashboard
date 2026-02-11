from flask import Blueprint, render_template, request, redirect, session, url_for
from database.models import User
from Suspicious_Login_Detection_system.ml_routes import predict_login_logic

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("login.html", error="Invalid username or password")

        # 🔎 Find user
        user = User.query.filter_by(username=username).first()

        # ❌ Wrong credentials
        if not user or not user.check_password(password):
            return render_template("login.html", error="Invalid username or password")

        # ✅ Correct credentials
        session["user_id"] = user.id

        # ---------------- ML CHECK ----------------
        data = {
            "login_attempts": 2,
            "ip_change": 1,
            "device_change": 0
        }

        result = predict_login_logic(data)

        # ✅ Store ML result
        session["ml_result"] = result

        print("ML Result:", result)

        # 🔴 Suspicious → Show Alert Page
        if result == "Suspicious Login":
            return render_template("alert.html")

        # 🟢 Normal → Dashboard
        return redirect(url_for("dashboard"))

    return render_template("login.html")


# ---------------- LOGOUT ----------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
