from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Server(db.Model):
    __tablename__ = "servers"

    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(120), nullable=False)
    host = db.Column(db.String(255), nullable=False)
    ssh_username = db.Column(db.String(120), nullable=False)
    auth_method = db.Column(db.String(20), nullable=False)  # password | key
    # Encrypted SSH password (Fernet) when auth_method=password; never log
    ssh_password_encrypted = db.Column(db.Text, nullable=True)
    # Filesystem path to private key when auth_method=key
    ssh_key_path = db.Column(db.String(512), nullable=True)
    ssh_port = db.Column(db.Integer, nullable=False, default=22)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
