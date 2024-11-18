# pylint: disable=E1101

"""
This module defines the database models for the application.

Models:
    User: Represents a user in the system.
    CardRequest: Represents a card request made by a user.
"""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


class User(db.Model):
    """
    A database model representing a user in the system.

    Attributes:
        id (int): The primary key for the user.
        username (str): The unique username of the user.
        password_hash (str): The hashed password of the user.
        card_requests (list): A list of card requests associated with the user.

    Methods:
        set_password(password): Hashes and sets the user's password.
        check_password(password): Verifies if the provided password matches the stored hash.
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Enable cascade delete by adding cascade="all, delete-orphan" to the relationship
    card_requests = db.relationship(
        "CardRequest", backref="user", cascade="all, delete-orphan", lazy=True
    )

    def set_password(self, password):
        """
        Hashes and sets the user's password.

        Args:
            password (str): The plaintext password to be hashed.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verifies if the provided password matches the stored hash.

        Args:
            password (str): The plaintext password to verify.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class CardRequest(db.Model):  # pylint: disable=too-few-public-methods
    """
    A database model representing a card request made by a user.

    Attributes:
        id (int): The primary key for the card request.
        user_id (int): The ID of the user making the card request.
        status (str): The status of the card request (default: "pending").
        created_at (datetime): The timestamp when the card request was created.
        updated_at (datetime): The timestamp when the card request was last updated.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    status = db.Column(db.String(20), default="pending", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<CardRequest {self.id} - {self.status}>"
