"""
My Service

Describe what your service does here
"""
from datetime import date
from flask import jsonify, request, url_for, abort
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
        jsonify(
            name="Recommendation REST API Service",
            version="1.0",
            paths=url_for("list_recommendations", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Place your REST API code here ...
######################################################################
# LIST ALL RECOMMENDATIONS (LIST)
######################################################################
@app.route("/recommendations", methods=["GET"])
def list_recommendations():
    """Returns all of the Recommendations"""
    app.logger.info("Request for recommendation list")
    recommendations = []

    product_id = request.args.get("product_id")
    user_id = request.args.get("user_id")
    bought_in_last_30d = request.args.get("bought_in_last_30d")
    recommendation_type = request.args.get("recommendation_type")

    if product_id:
        recommendations = Recommendation.find_by_product_id(product_id)
    elif user_id:
        recommendations = Recommendation.find_by_user_id(user_id)
    elif bought_in_last_30d:
        recommendations = Recommendation.find_by_bought_in_last_30d(bought_in_last_30d)
    elif recommendation_type:
        recommendations = Recommendation.find_by_recommendation_type(recommendation_type)
    else:
        recommendations = Recommendation.all()

    results = [recommendation.serialize()
               for recommendation in recommendations]
    app.logger.info("Returning %d recommendations", len(results))
    return jsonify(results), status.HTTP_200_OK


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
        return error_handlers.request_validation_error("No Data Provided")
    if not isinstance(request.json['user_id'], int):
        return error_handlers.request_validation_error("Invalid Data Type")
    recommendation.deserialize(request.get_json())
    recommendation.create()
    message = recommendation.serialize()
    location_url = url_for("get_recommendation", recommendation_id=recommendation.id, _external=True)

    app.logger.info("Recommendation with ID [%s] created.", recommendation.id)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# UPDATE A NEW RECOMMENDATION TYPE
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["PUT"])
def update_recommendations(recommendation_id):
    """
    Update a Recommendation
    This endpoint will update a Recommendation based the body that is posted
    """
    app.logger.info("Request to update recommendation with id: %s", recommendation_id)
    check_content_type("application/json")
    
    # Get the recommendation from the database
    recommendation = Recommendation.find(recommendation_id)
    # recommendation = Recommendation.query.get(recommendation_id)
    if not recommendation:
        abort(status.HTTP_404_NOT_FOUND,
              f"recommendation with id '{recommendation_id}' was not found.")
    # Get the original create date, so that it doesn't get updated
    create_date = recommendation.serialize()["create_date"]

    # Deserialize the incoming request's JSON data into the recommendation
    recommendation.deserialize(request.get_json())
    if recommendation.rating>5 or recommendation.rating<1:
        abort(status.HTTP_400_BAD_REQUEST,
              f"recommendation with rating '{recommendation.rating}' was not acceptable.")
    # recommendation.id = recommendation_id
    recommendation.update_date = date.today()
    recommendation.create_date = create_date
    recommendation.update()
    app.logger.info("Recommendation with ID [%s] updated.", recommendation.id)
    return jsonify(recommendation.serialize()), status.HTTP_200_OK


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


