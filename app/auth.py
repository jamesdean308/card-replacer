"""
This module provides authentication-related utilities.
"""

from .models import User


def authenticate_user(username, password):
    """
    Authenticate a user based on the provided username and password.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.

    Returns:
        Optional[User]: The authenticated user object if credentials are valid;
                        otherwise, None.
    """
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return None
