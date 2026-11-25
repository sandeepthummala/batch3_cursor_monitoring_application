from flask import Blueprint, current_app, render_template

from app.auth_utils import login_required
from app.extensions import db
from app.models import Server
from app.ssh import collect_metrics

bp = Blueprint("main", __name__)


@bp.route("/")
@login_required
def dashboard():
    servers = Server.query.order_by(Server.display_name).all()
    connect_timeout = current_app.config["SSH_CONNECT_TIMEOUT"]
    command_timeout = current_app.config["SSH_COMMAND_TIMEOUT"]
    cards = []
    for server in servers:
        metrics = collect_metrics(
            server,
            connect_timeout=connect_timeout,
            command_timeout=command_timeout,
        )
        cards.append({"server": server, "metrics": metrics})
    return render_template("dashboard.html", cards=cards)


@bp.route("/servers/<int:server_id>")
@login_required
def server_detail(server_id: int):
    server = db.get_or_404(Server, server_id)
    metrics = collect_metrics(
        server,
        connect_timeout=current_app.config["SSH_CONNECT_TIMEOUT"],
        command_timeout=current_app.config["SSH_COMMAND_TIMEOUT"],
    )
    return render_template("server_detail.html", server=server, metrics=metrics)
