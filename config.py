import os

# Change DB_PASSWORD to your own MySQL root password.
# (Or set an environment variable named DB_PASSWORD so the password is never saved in code.)
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = os.environ.get("DB_PASSWORD", "mansi@132006")
DB_NAME = "smart_tourism"

# Secret key used by Flask to sign the session cookie.
SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key-before-submission")
