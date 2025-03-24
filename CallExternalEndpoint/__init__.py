"""
# Function rendering
"""

import logging
import azure.functions as func
import requests
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/api/CallExternalEndpoint", methods=["GET"])
def call_external_endpoint():
    """The function"""
    try:
        # URL of the external endpoint you want to call
        # external_url = "https://external.endpoint/sample.json"

        # # Make a GET request to the external endpoint
        # response = requests.get(external_url)

        # # Check if the request was successful
        # response.raise_for_status()

        # Return the JSON response received from the external endpoint
        return jsonify(msg="Hello world")
    except requests.exceptions.ConnectionError as conn_err:
        # Handle errors due to connection problems, such as DNS failure, refused connection, etc.
        logging.error(f"Connection error occurred: {conn_err}")
        return (
            jsonify({"error": "Connection error occurred", "details": str(conn_err)}),
            502,
        )
    except requests.exceptions.HTTPError as http_err:
        # Handle HTTP errors that occur
        # because of unsuccessful HTTP response codes
        logging.error(f"HTTP error occurred: {http_err}")
        return jsonify({"error": "HTTP error occurred", "details": str(http_err)}), 500
    except requests.exceptions.RequestException as req_err:
        # Handle other requests-related errors (e.g., network issues)
        logging.error(f"Request error occurred: {req_err}")
        return (
            jsonify({"error": "Request error occurred", "details": str(req_err)}),
            500,
        )
    except Exception as err:
        # Handle any other exceptions
        logging.error(f"An error occurred: {err}")
        return jsonify({"error": "An error occurred", "details": str(err)}), 500


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """
    # Delegate the request handling to Flask
    """
    logging.debug("main  triggered")
    return func.WsgiMiddleware(app.wsgi_app).handle(req, context)
