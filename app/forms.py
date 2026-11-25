import re

from flask_wtf import FlaskForm
from wtforms import IntegerField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError

_HOST_RE = re.compile(r"^[A-Za-z0-9._:\-\[\]]+$")


def validate_host(form, field):  # noqa: ARG001
    value = (field.data or "").strip()
    if not value or not _HOST_RE.match(value) or any(c.isspace() for c in value):
        raise ValidationError("Invalid host (letters, digits, . _ - : [ ] only).")
    if ";" in value or "|" in value or "`" in value or "$" in value:
        raise ValidationError("Invalid host characters.")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("Password", validators=[DataRequired(), Length(max=256)])
    submit = SubmitField("Sign in")


class ServerForm(FlaskForm):
    display_name = StringField(
        "Display name", validators=[DataRequired(), Length(max=120)]
    )
    host = StringField(
        "Hostname / IP", validators=[DataRequired(), Length(max=255), validate_host]
    )
    ssh_username = StringField(
        "SSH username", validators=[DataRequired(), Length(max=120)]
    )
    auth_method = SelectField(
        "Auth method",
        choices=[("password", "Password"), ("key", "Private key path")],
        validators=[DataRequired()],
    )
    ssh_password = PasswordField("SSH password", validators=[Optional(), Length(max=512)])
    ssh_key_path = StringField(
        "Private key path", validators=[Optional(), Length(max=512)]
    )
    ssh_port = IntegerField(
        "SSH port",
        default=22,
        validators=[DataRequired(), NumberRange(min=1, max=65535)],
    )
    submit = SubmitField("Save")
    test_connection = SubmitField("Test connection")

    def validate(self, extra_validators=None):
        ok = super().validate(extra_validators=extra_validators)
        if not ok:
            return False
        if self.auth_method.data == "password":
            # On edit, empty password means keep existing
            if not self.ssh_password.data and not getattr(self, "_allow_blank_password", False):
                self.ssh_password.errors.append("SSH password is required.")
                return False
        elif self.auth_method.data == "key":
            if not (self.ssh_key_path.data or "").strip():
                self.ssh_key_path.errors.append("Private key path is required.")
                return False
        return True


class DeleteServerForm(FlaskForm):
    submit = SubmitField("Delete")
