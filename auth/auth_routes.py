from flask import Blueprint, render_template, request, redirect, session, url_for
from database.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("login.html", error="Invalid username or password")

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return render_template("login.html", error="Invalid username or password")

        # ✅ Login Successful
        session["user_id"] = user.id

        # 🔥 After every login → show alert page
        return render_template("alert.html")

    return render_template("login.html")


# ---------------- LOGOUT ----------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
