from flask import Blueprint, current_app, flash, redirect, render_template, url_for

from app.auth_utils import login_required
from app.crypto_util import encrypt_secret
from app.extensions import db
from app.forms import DeleteServerForm, ServerForm
from app.models import Server
from app.ssh import check_ssh_connection

bp = Blueprint("servers", __name__, url_prefix="/servers")


def _apply_form_to_server(form: ServerForm, server: Server, *, is_edit: bool) -> None:
    server.display_name = form.display_name.data.strip()
    server.host = form.host.data.strip()
    server.ssh_username = form.ssh_username.data.strip()
    server.auth_method = form.auth_method.data
    server.ssh_port = form.ssh_port.data or 22

    if form.auth_method.data == "password":
        server.ssh_key_path = None
        if form.ssh_password.data:
            server.ssh_password_encrypted = encrypt_secret(form.ssh_password.data)
        elif not is_edit:
            server.ssh_password_encrypted = None
    else:
        server.ssh_password_encrypted = None
        server.ssh_key_path = (form.ssh_key_path.data or "").strip() or None


@bp.route("/")
@login_required
def list_servers():
    servers = Server.query.order_by(Server.display_name).all()
    return render_template("servers/list.html", servers=servers)


@bp.route("/add", methods=["GET", "POST"])
@login_required
def add_server():
    form = ServerForm()
    if form.validate_on_submit():
        server = Server()
        _apply_form_to_server(form, server, is_edit=False)

        if form.test_connection.data:
            result = check_ssh_connection(
                server, timeout=current_app.config["SSH_CONNECT_TIMEOUT"]
            )
            flash(result.message, "success" if result.ok else "danger")
            return render_template("servers/form.html", form=form, title="Add server")

        db.session.add(server)
        db.session.commit()
        flash("Server added.", "success")
        return redirect(url_for("servers.list_servers"))

    return render_template("servers/form.html", form=form, title="Add server")


@bp.route("/<int:server_id>/edit", methods=["GET", "POST"])
@login_required
def edit_server(server_id: int):
    server = db.get_or_404(Server, server_id)
    form = ServerForm(obj=server)
    form._allow_blank_password = True

    if form.validate_on_submit():
        _apply_form_to_server(form, server, is_edit=True)

        if form.test_connection.data:
            result = check_ssh_connection(
                server, timeout=current_app.config["SSH_CONNECT_TIMEOUT"]
            )
            flash(result.message, "success" if result.ok else "danger")
            return render_template(
                "servers/form.html",
                form=form,
                title="Edit server",
                server=server,
            )

        db.session.commit()
        flash("Server updated.", "success")
        return redirect(url_for("servers.list_servers"))

    if form.auth_method.data == "key":
        form.ssh_key_path.data = server.ssh_key_path
    # Never prefill password fields
    form.ssh_password.data = ""

    return render_template(
        "servers/form.html", form=form, title="Edit server", server=server
    )


@bp.route("/<int:server_id>/delete", methods=["GET", "POST"])
@login_required
def delete_server(server_id: int):
    server = db.get_or_404(Server, server_id)
    form = DeleteServerForm()
    if form.validate_on_submit():
        db.session.delete(server)
        db.session.commit()
        flash("Server deleted.", "info")
        return redirect(url_for("servers.list_servers"))
    return render_template("servers/confirm_delete.html", form=form, server=server)


@bp.route("/<int:server_id>/test", methods=["POST"])
@login_required
def test_server(server_id: int):
    server = db.get_or_404(Server, server_id)
    form = DeleteServerForm()  # CSRF-only POST body
    if form.validate_on_submit():
        result = check_ssh_connection(
            server, timeout=current_app.config["SSH_CONNECT_TIMEOUT"]
        )
        flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("servers.list_servers"))
