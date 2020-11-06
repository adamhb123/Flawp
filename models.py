from modules import db, bcrypt
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.Binary(60), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    date_created = db.Column(db.Text, default=datetime.now().strftime("%Y-%m-%d"))
    birthday = db.Column(db.Text, nullable=False)
    authenticated = False

    def __init__(self, username, password, name, birthday):
        self.username = username
        self.password = bcrypt.generate_password_hash(password)
        self.name = name
        self.birthday = birthday

    #   The following are all required for flask-login
    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return self.authenticated

    def get_id(self):
        return self.id


class Flaw(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(20), nullable=False)
    long_name = db.Column(db.String(80), server_default=short_name)
    description = db.Column(db.String(1000), server_default="No description provided...")


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    short_description = db.Column(db.String(100))
    long_description = db.Column(db.String(1000))
