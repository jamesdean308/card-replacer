# app/tasks.py
import os
import time

from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .models import CardRequest

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

celery = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


@celery.task
def process_card_request(request_id):
    session = Session()
    try:
        card_request = session.query(CardRequest).get(request_id)
        if card_request:

            time.sleep(10)  # Simulate processing time

            card_request.status = "processed"
            session.commit()
            return "Card request processed successfully"
        return "Card request not found"
    except Exception as e:
        session.rollback()
        return f"Error processing card request: {str(e)}"
    finally:
        session.close()


@celery.task
def add(x, y):
    return x + y
