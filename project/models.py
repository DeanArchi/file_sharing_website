from datetime import datetime

from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    """
        User model represents a user in the application.

        Fields:
            id: Unique identifier for the user
            username: User's unique username
            password: User's hashed password
            name: Full name of the user
            is_admin: Boolean flag to mark admin users
            downloads: Relationship to the download logs associated with the user
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    is_admin = db.Column(db.Boolean, default=False)
    downloads = db.relationship('DownloadLog', backref='user', lazy=True)

    def __init__(self, username, name, password):
        self.username = username
        self.name = name
        self.password = password


class File(db.Model):
    """
        File model represents a file in the application.

        Fields:
            id: Unique identifier for the file
            filename: Name of the file
            path: Path where the file is stored
            upload_date: Date and time when the file was uploaded
            download_count: Number of times the file has been downloaded
    """
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), unique=True, nullable=False)
    path = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    download_count = db.Column(db.Integer, default=0)


class FileAccess(db.Model):
    """
        FileAccess model stores file permissions for users.

        Fields:
            id: Unique identifier for the record
            user_id: Reference to the user
            file_id: Reference to the file
            permission: Boolean indicating if the user has permission to access the file
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
    permission = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref=db.backref('file_access', lazy=True))
    file = db.relationship('File', backref=db.backref('file_access', lazy=True))

    def __init__(self, user_id, file_id, permission):
        self.user_id = user_id
        self.file_id = file_id
        self.permission = permission


class DownloadLog(db.Model):
    """
        DownloadLog model stores logs of user file downloads.

        Fields:
            id: Unique identifier for the log
            user_id: Reference to the user who downloaded the file
            file_id: Reference to the file that was downloaded
            timestamp: Date and time of the download
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
