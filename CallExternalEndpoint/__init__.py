"""
# Function rendering
"""

import logging
import azure.functions as func
from flask import Flask, jsonify

# Database configuration (replace with your actual database URI)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError

app = Flask(__name__)
# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Avoids a warning

# Create SQLAlchemy instance
db = SQLAlchemy(app)


class Profile(db.Model):
    """
    Profile model
    """

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), unique=False, nullable=False)
    last_name = db.Column(db.String(20), unique=False, nullable=False)
    age = db.Column(db.Integer, nullable=False)

    # repr method represents how one object of this datatable
    # will look like
    def __repr__(self):
        return f"Name : {self.first_name}, Age: {self.age}"


@app.route("/api/CallExternalEndpoint", methods=["GET"])
def call_external_endpoint():
    """The function"""
    try:
        profiles = Profile.query.all()
        return jsonify(users=profiles)
    except IntegrityError as ie:
        # Handle exceptions related to integrity constraints, like unique constraints
        logging.error("Integrity error occurred: %s", ie)
        return jsonify(msg="Integrity error"), 400

    except OperationalError as oe:
        # Handle operational errors, like issues connecting to the database
        logging.error("Operational error occurred: %s", oe)
        return jsonify(msg="Operational error"), 500

    except SQLAlchemyError as sa_err:
        # Catch-all for other SQLAlchemy-related exceptions
        logging.error("Database error occurred: %s", sa_err)
        return jsonify(msg="Database error"), 500


def profile():
    """
    # Add Profile to db
    """
    first_name = "first_name"
    last_name = "last_name"
    age = "age"

    if first_name != "" and last_name != "" and age is not None:
        p = Profile(first_name=first_name, last_name=last_name, age=age)
        db.session.add(p)
        db.session.commit()
        return jsonify(msg="Operation completed"), 200
    else:
        return jsonify(msg="Operation failed"), 400


def erase():
    """
    # Delete Profile to db
    """
    data = Profile.query.get(1)
    db.session.delete(data)
    db.session.commit()
    return jsonify(msg="Operation completed"), 200


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """
    # Delegate the request handling to Flask
    """
    with app.app_context():  # Needed for DB operations
        db.create_all()  # Creates the database and tables
    return func.WsgiMiddleware(app.wsgi_app).handle(req, context)
