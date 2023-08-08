"""
Pet Store Service with Swagger

Paths:
------
GET / - Displays a UI for Selenium testing
GET /recommendations - Returns a list all of the recommendations
GET /recommendations/{recommendation_id} - Returns the recommendations with a given id number
POST /recommendations - creates a new recommendation record in the database
PUT /recommendations/{id} - updates a recommendation record in the database
DELETE /recommendations/{id} - deletes a recommendation record in the database
"""
from datetime import date
from flask import request, url_for, abort
from flask_restx import Resource, fields, reqparse, inputs
from service.common import status  # HTTP Status Codes
from service.models import Recommendation, RecommendationType

# from service.common import error_handlers

# Import Flask application
from . import app, api


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return {"status": 'OK'}, status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """
    Base URL for our service
    """
    return app.send_static_file("index.html")
# Define the model so that the docs reflect what can be sent


create_model = api.model(
    "Recommendations",
    {
        "user_id": fields.Integer(
            required=True,
            description="The user_id",
            ),
        "product_id": fields.Integer(
            required=True, description="The product_id"
            ),
        # pylint: disable=protected-access
        "bought_in_last_30_days": fields.Boolean(
            required=True,
            description="Has the user bought the product in the last 30 days?",
            ),
        "rating": fields.Integer(
            required=False,
            description="The rating for the recommendation (0 to 5)",
            ),
        "recommendation_type": fields.String(
            required=True,
            enum=RecommendationType._member_names_,
            description="The type of recommendation (i.e UPSELL , CROSS SELL, TRENDING , FREQ_BOUGHT_TOGETHER, RECOMMENDED_FOR_YOU, UNKNOWN)",
            ),
    }
)

recommendation_model = api.inherit(
    "RecommendationModel",
    create_model,
    {
        "id": fields.Integer(
            readOnly=True, description="The unique id assigned internally by service"
        )
    },
)

# query string arguments
recommendation_args = reqparse.RequestParser()
recommendation_args.add_argument(
    "user_id", type=int, location="args", required=False, help="List Recommendations for the user_id"
)


######################################################################
#  PATH: /recommendations/{recommendation_id}
######################################################################
@api.route("/recommendations/<recommendation_id>")
@api.param("recommendation_id", "The recommendation identifier")
class RecommendationResource(Resource):
    """
    RecommendationResource class

    Allows the manipulation of a single Recommendation
    GET /recommendation{id} - Returns a recommendation with the id
    PUT /recommendation{id} - Update a recommendation with the id
    DELETE /recommendation{id} -  Deletes a recommendation with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc("get_recommendations")
    @api.response(404, "Recommendation not found")
    @api.marshal_with(recommendation_model)
    def get(self, recommendation_id):
        """
        Retrieve a single recommendation
        This endpoint will return a recommendation based on its id
        """
        app.logger.info("Request for recommendation with id: %s", recommendation_id)
        recommendation = Recommendation.find(recommendation_id)
        if not recommendation:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"recommendation with id '{recommendation_id}' was not found.",
            )

        app.logger.info("Returning recommendation: %s", recommendation.user_id)
        return recommendation.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc("update_recommendations")
    @api.response(404, "Recommendation not found")
    @api.response(400, "The posted recommendation data was not valid")
    @api.expect(recommendation_model)
    @api.marshal_with(recommendation_model)
    def put(self, recommendation_id):
        """
        Update a Recommendation
        This endpoint will update a Recommendation based the body that is posted
        """
        app.logger.info("Request to update recommendation with id: %s", recommendation_id)
        
        # Get the recommendation from the database
        recommendation = Recommendation.find(recommendation_id)
        app.logger.debug("Payload = %s", api.payload)
        if not recommendation:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"recommendation with id '{recommendation_id}' was not found.",
            )
        # Get the original create date, so that it doesn't get updated
        create_date = recommendation.serialize()["create_date"]
        
        # Get the original rating, so that it doesn't get updated
        rating_original = recommendation.serialize()["rating"]

        # Deserialize the incoming payload into the recommendation
        data = api.payload
        recommendation.deserialize(data)

        recommendation.id = recommendation_id
        if recommendation.rating is not None:
            if recommendation.rating > 5 or recommendation.rating < 0:
                abort(
                    status.HTTP_400_BAD_REQUEST,
                    f"recommendation with rating '{recommendation.rating}' was not acceptable.",
                )
        recommendation.rating = rating_original
        recommendation.update_date = date.today()
        recommendation.create_date = create_date
        recommendation.update()
        app.logger.info("Recommendation with ID [%s] updated.", recommendation.id)
        return recommendation.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc("delete_recommendations")
    @api.response(204, "Recommendation deleted")
    def delete(self, recommendation_id):
        """
        Delete a recommendation
        This endpoint will delete a Recommendation with the specified id
        """
        app.logger.info("Request to delete a recommendation_id %s", recommendation_id)
        recommendation = Recommendation.find(recommendation_id)
        if recommendation:
            recommendation.delete()
        app.logger.info("Recommendation with ID %s delete complete.", recommendation_id)
        return "", status.HTTP_204_NO_CONTENT

######################################################################
#  PATH: /recommendations
######################################################################


@api.route("/recommendations", strict_slashes=False)
class RecommendationCollection(Resource):
    """Handles all interactions with collections of Recommendations"""

    # ------------------------------------------------------------------
    # LIST ALL RECOMMENDATIONS
    # ------------------------------------------------------------------
    @api.doc("list_recommendations")
    @api.expect(recommendation_args, validate=True)
    @api.marshal_list_with(recommendation_model)
    def get(self):
        """Returns all of the Recommendations"""
        app.logger.info("Request for recommendation list")
        recommendations = []

        args = recommendation_args.parse_args()

        if args["user_id"]:
            recommendations = Recommendation.find_by_user_id(args["user_id"])
        else:
            recommendations = Recommendation.all()

        results = [recommendation.serialize() for recommendation in recommendations]
        app.logger.info("Returning %d recommendations", len(results))
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc("create_recommendations")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_model)
    @api.marshal_with(recommendation_model, code=201)
    def post(self):
        """
        Creates a Recommendation
        This endpoint will create a Recommendation based the data in the body that is posted
        """
        app.logger.info("Request to create a recommendation")
        # check_content_type("application/json")
        recommendation = Recommendation()
        app.logger.debug("Payload = %s", api.payload)
        recommendation.deserialize(api.payload)
        recommendation.create()
        location_url = api.url_for(
            RecommendationResource, recommendation_id=recommendation.id, _external=True
        )

        app.logger.info("Recommendation with ID [%s] created.", recommendation.id)
        return recommendation.serialize(), status.HTTP_201_CREATED, {"Location": location_url}

######################################################################
#  PATH: /recommendations/{recommendation_id}/rating
######################################################################


@api.route("/recommendations/<recommendation_id>/rating")
@api.param("recommendation_id", "The Recommendation identifier")
class RatingResource(Resource):
    """Rating actions on a Recommendation"""

    @api.doc("rating_recommendations")
    @api.response(404, "recommendation not found")
    @api.response(409, "The Recommendation is not available for rating")
    def put(self, recommendation_id):
        """
        Rate a Recommendation
        This endpoint will rate a Recommendation
        """
        app.logger.info("Request to update recommendation rating with id: %s", recommendation_id)

        # Get the recommendation from the database
        recommendation = Recommendation.find(recommendation_id)
        if not recommendation:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Recommendation with id '{recommendation_id}' was not found.",
            )

        data = api.payload
        rating = data["rating"]

        # rating = request.get_json().get("rating")
        if rating is not None and isinstance(rating, int) and 0 <= rating <= 5:
            recommendation.rating = rating
            recommendation.update()
        else:
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Rating must be an integer between 0 and 5 (inclusive).",
            )

        app.logger.info("Recommendation rating with ID [%s] updated.", recommendation.id)
        return recommendation.serialize(), status.HTTP_200_OK
