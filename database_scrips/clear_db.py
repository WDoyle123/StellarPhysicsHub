import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app import app, db

with app.app_context():
    db.drop_all()
    db.create_all()

print("Database cleared and reinitialised.")

