from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    permissions = db.Column(db.String(128))
    can_watch = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(64))
    name = db.Column(db.String(64))
    number = db.Column(db.String(64))
    timestamp_added = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    timestamp_added_accepted = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    filepath = db.Column(db.String(64))
    key_words = db.Column(db.String(1024))

    def __repr__(self):
        return '<File {}>'.format(self.body)


