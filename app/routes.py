# pylint: disable=E1101

"""
This module defines the routes for the Flask application, including endpoints for
user registration, login, card requests, task management, and user deletion.

Routes:
- /add: Adds two numbers asynchronously.
- /tasks/<task_id>: Retrieves the status and result of an asynchronous task.
- /register: Registers a new user.
- /login: Authenticates a user and returns access and refresh tokens.
- /refresh: Refreshes the access token.
- /request_card: Submits a new card request asynchronously.
- /card_requests: Retrieves all card requests for the authenticated user.
- /delete_user: Deletes the authenticated user account.
"""

from celery.result import AsyncResult
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .auth import authenticate_user
from .models import CardRequest, User, db
from .tasks import add, process_card_request

main = Blueprint("main", __name__)


@main.route("/add", methods=["POST"])
def add_route():
    """
    Add two numbers asynchronously.

    The input JSON should contain `x` and `y`, representing the numbers to add.

    Returns:
        JSON response with the task ID of the asynchronous addition.
    """
    data = request.get_json()
    x = data.get("x")
    y = data.get("y")
    result = add.delay(x, y)
    return jsonify({"task_id": result.id}), 202


@main.route("/tasks/<task_id>", methods=["GET"])
def get_task_status(task_id):
    """
    Get the status and result of an asynchronous task.

    Args:
        task_id (str): The ID of the task.

    Returns:
        JSON response with the task ID, status, and result.
    """
    result = AsyncResult(task_id)

    if result.failed():
        response = {
            "task_id": task_id,
            "status": result.status,
            "result": str(result.result),
        }
    else:
        response = {
            "task_id": task_id,
            "status": result.status,
            "result": result.result,
        }

    return jsonify(response), 200


@main.route("/register", methods=["POST"])
def register():
    """
    Register a new user.

    The input JSON should contain `username` and `password`.

    Returns:
        JSON response indicating the registration status.
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 400

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully"}), 201


limiter = Limiter(key_func=get_remote_address)


@main.route("/login", methods=["POST"])
@limiter.limit("5 per minute")  # Allow 5 login attempts per minute per IP address
def login():
    """
    Log in a user and return access and refresh tokens.

    The input JSON should contain `username` and `password`.

    Returns:
        JSON response with access and refresh tokens or an error message.
    """
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"msg": "Missing username or password"}), 400

    username = data.get("username")
    password = data.get("password")

    user = authenticate_user(username, password)
    if not user:
        return jsonify({"msg": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200


@main.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh the access token for the current user.

    Returns:
        JSON response with the new access token.
    """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify(access_token=access_token), 200


@main.route("/request_card", methods=["POST"])
@jwt_required()
def request_card():
    """
    Submit a new card request asynchronously.

    Returns:
        JSON response indicating the submission status or an error message.
    """
    user_id = get_jwt_identity()

    pending_request = CardRequest.query.filter_by(
        user_id=user_id, status="pending"
    ).first()
    if pending_request:
        return (
            jsonify(
                {
                    "msg": "You already have a pending card request. "
                    "Please wait until it is processed."
                }
            ),
            400,
        )

    new_request = CardRequest(user_id=user_id)
    db.session.add(new_request)
    db.session.commit()

    task = process_card_request.delay(new_request.id)

    return jsonify({"msg": "Card request submitted", "task_id": task.id}), 201


@main.route("/card_requests", methods=["GET"])
@jwt_required()
def get_card_requests():
    """
    Retrieve all card requests for the authenticated user.

    Returns:
        JSON response with a list of card requests.
    """
    user_id = get_jwt_identity()
    requests = CardRequest.query.filter_by(user_id=user_id).all()

    return jsonify(
        [
            {
                "id": req.id,
                "status": req.status,
                "created_at": req.created_at,
                "updated_at": req.updated_at,
            }
            for req in requests
        ]
    )


@main.route("/delete_user", methods=["DELETE"])
@jwt_required()
def delete_user():
    """
    Delete the authenticated user's account.

    Returns:
        JSON response indicating the deletion status.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"msg": "User deleted successfully"}), 200
