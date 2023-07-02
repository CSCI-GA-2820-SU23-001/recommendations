"""
My Service

Describe what your service does here
"""

from flask import Flask, jsonify, request, url_for, make_response, abort
from service.common import status  # HTTP Status Codes
from service.models import Recommendation
from service.common import error_handlers

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Place your REST API code here ...

######################################################################
# RETRIEVE A RECOMMENDATION (READ)
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["GET"])
def get_recommendation(recommendation_id):
    """
    Retrieve a single recommendation
    This endpoint will return a recommendation based on its id
    """
    app.logger.info("Request for recommendation with id: %s", recommendation_id)
    recommendation = Recommendation.find(recommendation_id)
    if not recommendation:
        abort(status.HTTP_404_NOT_FOUND,
              f"recommendation with id '{recommendation_id}' was not found.")

    app.logger.info("Returning recommendation: %s",
                    recommendation.user_id)
    return jsonify(recommendation.serialize()), status.HTTP_200_OK

######################################################################
# ADD A NEW RECOMMENDATION
######################################################################
@app.route("/recommendations", methods=["POST"])
def create_recommendations():
    """
    Creates a Recommendation
    This endpoint will create a Recommendation based the data in the body that is posted
    """
    app.logger.info("Request to create a recommendation")
    check_content_type("application/json")
    recommendation = Recommendation()
    if not request.json:
        return jsonify({'message': 'Bad Request. No data provided'}), status.HTTP_400_BAD_REQUEST
    if not isinstance(request.json['user_id'], int):
        return error_handlers.request_validation_error("Invalid Data Type")
    recommendation.deserialize(request.get_json())
    recommendation.create()
    message = recommendation.serialize()
    #location_url = url_for("recommendations", recommendation_id=recommendation.id, _external=True) ## TODO

    app.logger.info("Recommendation with ID [%s] created.", recommendation.id)
    return jsonify(message), status.HTTP_201_CREATED


######################################################################
# DELETE A RECOMMENDATION
######################################################################

@app.route("/recommendations/<int:recommendation_id>", methods=["DELETE"])
def delete_recommendation(recommendation_id):
    '''This endpoint will delete a Recommendation with the specified id'''
    app.logger.info("Request to delete a recommendation_id %s", recommendation_id)
    recommendation_id = Recommendation.find(recommendation_id)
    if recommendation_id:
        recommendation_id.delete()
    
    app.logger.info("Recommendation with ID %s delete complete.", recommendation_id)
    return "", status.HTTP_204_NO_CONTENT




######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


    
