from flask import Flask

from app.config import Config
from app.extensions import csrf, db
from app.models import User


def create_app(config_object=None) -> Flask:
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(config_object or Config)

    db.init_app(app)
    csrf.init_app(app)

    from app.routes.api import bp as api_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.main import bp as main_bp
    from app.routes.servers import bp as servers_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(servers_bp)
    app.register_blueprint(api_bp)

    @app.context_processor
    def inject_globals():
        from flask import session

        return {"current_username": session.get("username")}

    with app.app_context():
        db.create_all()
        _seed_admin(app)

    return app


def _seed_admin(app: Flask) -> None:
    username = app.config["DEMO_ADMIN_USERNAME"]
    if User.query.filter_by(username=username).first():
        return
    user = User(username=username)
    user.set_password(app.config["DEMO_ADMIN_PASSWORD"])
    db.session.add(user)
    db.session.commit()
