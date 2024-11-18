# app/tasks.py

"""
This module defines Celery tasks for processing card requests and
handling database operations using SQLAlchemy.

Tasks:
- process_card_request: Processes a card request by updating its status.
- add: A simple addition task for testing purposes.
"""

import os
import subprocess

from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from .models import CardRequest

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
DATABASE_URL = os.getenv("DATABASE_URL")

celery = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


class DatabaseTask(celery.Task):
    """
    A custom Celery task base class that manages SQLAlchemy sessions.

    This class ensures that each Celery task has its own SQLAlchemy session,
    which is created before the task starts and cleaned up after it completes.

    Attributes:
        sessions (dict): A mapping of task IDs to their respective SQLAlchemy sessions.
    """

    def __init__(self):
        self.sessions = {}

    def before_start(self, task_id, args, kwargs):
        """Create a new session before the task starts."""
        self.sessions[task_id] = Session()
        super().before_start(task_id, args, kwargs)

    def after_return(
        self, status, retval, task_id, args, kwargs, einfo
    ):  # pylint: disable=too-many-arguments, too-many-positional-arguments
        """Close and clean up the session after the task ends."""
        session = self.sessions.pop(task_id, None)
        if session:
            session.close()
        super().after_return(status, retval, task_id, args, kwargs, einfo)

    @property
    def session(self):
        """Return the session associated with the current task request."""
        return self.sessions[self.request.id]


@celery.task(base=DatabaseTask)
def process_card_request(request_id):
    """
    Process a card request by updating its status in the database.

    Args:
        request_id (int): The ID of the card request to process.

    Returns:
        str: A message indicating the result of the processing.
    """
    session = process_card_request.session
    try:
        card_request = session.query(CardRequest).get(request_id)
        if card_request:
            # Simulate some CPU and I/O stress using stress-ng
            # '--cpu 2' simulates two CPU workers running tasks.
            # '--io 2' simulates two I/O workers generating I/O stress.
            # '--timeout 10s' limits the stress test duration to 10 seconds.
            subprocess.run(
                ["stress-ng", "--cpu", "2", "--io", "2", "--timeout", "10s"], check=True
            )

            card_request.status = "processed"
            session.commit()
            return "Card request processed successfully"
        return "Card request not found"
    except (SQLAlchemyError, subprocess.CalledProcessError) as e:
        session.rollback()
        return f"Error processing card request: {str(e)}"


# NOTE this doesn't really belong here, but makes for a good sanity check
@celery.task
def add(x, y):
    """
    A simple addition task for testing Celery.

    Args:
        x (int): The first number.
        y (int): The second number.

    Returns:
        int: The sum of x and y.
    """
    return x + y
