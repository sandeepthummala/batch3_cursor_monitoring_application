from flask import Blueprint, current_app, jsonify, session

from app.auth_utils import login_required
from app.extensions import db
from app.models import Server
from app.ssh import collect_metrics

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/servers/<int:server_id>/metrics")
@login_required
def server_metrics(server_id: int):
    # Auth via session cookie; never include credentials in JSON
    _ = session.get("user_id")
    server = db.get_or_404(Server, server_id)
    metrics = collect_metrics(
        server,
        connect_timeout=current_app.config["SSH_CONNECT_TIMEOUT"],
        command_timeout=current_app.config["SSH_COMMAND_TIMEOUT"],
    )
    payload = metrics.to_dict()
    payload["server_id"] = server.id
    payload["display_name"] = server.display_name
    return jsonify(payload)


@bp.route("/dashboard/metrics")
@login_required
def dashboard_metrics():
    connect_timeout = current_app.config["SSH_CONNECT_TIMEOUT"]
    command_timeout = current_app.config["SSH_COMMAND_TIMEOUT"]
    items = []
    for server in Server.query.order_by(Server.display_name).all():
        metrics = collect_metrics(
            server,
            connect_timeout=connect_timeout,
            command_timeout=command_timeout,
        )
        data = metrics.to_dict()
        data["server_id"] = server.id
        data["display_name"] = server.display_name
        data["host"] = server.host
        items.append(data)
    return jsonify({"servers": items})
