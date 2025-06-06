import requests
from email_validator import validate_email, EmailNotValidError
from flask import redirect, render_template, session
from functools import wraps
import re
from functools import wraps
import sqlite3
import os


def get_con_connection():
    db_path = os.path.abspath("users.db")
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con

def require_profile_completion(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return redirect("/login")

        con = get_con_connection()
        user = con.execute("SELECT username, gender, birthday FROM users WHERE id = ?", (user_id,)).fetchone()
        con.close()
        
        print(dict(user))

        if not user["username"] or not user["gender"] or not user["birthday"]:
            return redirect("/profile")
        
        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def is_valid_email(email):
    try:
        # Validar el correo
        validate_email(email)
        return True
    except EmailNotValidError as e:
        # Retorna False si no es válido
        return False


def is_secure_password(password):
    # Al menos 8 caracteres, un número, una letra mayúscula y un carácter especial
    password_regex = r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(password_regex, password) is not None
