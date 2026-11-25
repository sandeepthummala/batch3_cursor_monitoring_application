from flask import Blueprint, flash, redirect, render_template, session, url_for

from app.forms import LoginForm
from app.models import User

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.check_password(form.password.data):
            session.clear()
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("main.dashboard"))
        flash("Invalid username or password.", "danger")

    return render_template("login.html", form=form)


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Signed out.", "info")
    return redirect(url_for("auth.login"))
