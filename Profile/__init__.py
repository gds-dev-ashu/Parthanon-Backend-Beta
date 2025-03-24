"""
# Function rendering
"""

import logging
import azure.functions as func
from flask import Flask, jsonify, request

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
    email = db.Column(db.String(20), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)

    # This method represents how one object of this datatable
    # will look like
    def to_dict(self):
        """
        Parse Dict to serializable format.
        """
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "age": self.age,
        }


@app.route("/api/profile", methods=["GET"])
def fetch_all():
    """
    # Fetch Profile from db
    """
    try:
        profiles = Profile.query.all()
        profiles_list = [profile.to_dict() for profile in profiles]
        return jsonify(profiles_list)
    except IntegrityError as ie:
        # Roll back the session in case of an integrity error (e.g., duplicate entry)
        db.session.rollback()
        return jsonify(msg=f"Operation failed: Integrity error - {ie}"), 400

    except SQLAlchemyError as sa_err:
        # Roll back the session for any other database-related exceptions
        db.session.rollback()
        return jsonify(msg=f"Operation failed: Database error - {sa_err}"), 500

    except Exception as err:
        # Catch any other exceptions that are not related to the database
        return jsonify(msg=f"Operation failed: Unexpected error - {err}"), 500


@app.route("/api/profile/<int:profile_id>", methods=["GET"])
def fetch_one(profile_id):
    """
    # Fetch Profile from db
    """
    try:
        profiles = Profile.query.get(profile_id)
        return jsonify(profile=profiles.to_dict())
    except IntegrityError as ie:
        # Roll back the session in case of an integrity error (e.g., duplicate entry)
        db.session.rollback()
        return jsonify(msg=f"Operation failed: Integrity error - {ie}"), 400

    except SQLAlchemyError as sa_err:
        # Roll back the session for any other database-related exceptions
        db.session.rollback()
        return jsonify(msg=f"Operation failed: Database error - {sa_err}"), 500

    except Exception as err:
        # Catch any other exceptions that are not related to the database
        return jsonify(msg=f"Operation failed: Unexpected error - {err}"), 500


@app.route("/api/profile", methods=["POST"])
def create_profile():
    """
    # Add Profile to db
    """
    data = request.get_json()
    first_name = data["first_name"]
    last_name = data["last_name"]
    age = data["age"]
    email = data["email"]

    try:
        if first_name != "" and last_name != "" and age is not None and email != "":
            p = Profile(
                first_name=first_name, last_name=last_name, age=age, email=email
            )
            db.session.add(p)
            db.session.commit()
            return jsonify(msg="Operation completed"), 200
        else:
            return jsonify(msg="Operation failed"), 400

    except IntegrityError as ie:
        # Roll back the session in case of an integrity error (e.g., duplicate entry)
        db.session.rollback()
        return (
            jsonify(msg=f"Operation failed: Integrity error - {ie._sql_message}"),
            400,
        )

    except SQLAlchemyError as sa_err:
        # Roll back the session for any other database-related exceptions
        db.session.rollback()
        return jsonify(msg=f"Operation failed: Database error - {sa_err._message}"), 500

    except Exception as err:
        # Catch any other exceptions that are not related to the database
        return jsonify(msg=f"Operation failed: Unexpected error - {err}"), 500


@app.route("/api/profile/<int:profile_id>", methods=["PUT"])
def update(profile_id):
    """
    # Update Profile to db
    """
    data = request.get_json()
    age = data["age"]
    email = data["email"]

    if email != "" and age is not None:
        p = Profile.query.filter_by(id=profile_id).first()
        p.email = email
        p.age = age
        db.session.commit()
        return jsonify(msg="Operation completed"), 200
    else:
        return jsonify(msg="Operation failed"), 400


@app.route("/api/profile/<int:profile_id>", methods=["DELETE"])
def erase(profile_id):
    """
    # Delete Profile to db
    """
    data = Profile.query.get(profile_id)
    db.session.delete(data)
    db.session.commit()
    return jsonify(msg="Operation completed"), 200


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """
    # Delegate the request handling to Flask
    """
    with app.app_context():  # Needed for DB operations
        # db.drop_all()  # Creates the database and tables
        db.create_all()  # Creates the database and tables
    return func.WsgiMiddleware(app.wsgi_app).handle(req, context)
