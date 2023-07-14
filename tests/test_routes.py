"""
TestRecommendation API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging

# from logging import Formatter
from unittest import TestCase

# from unittest.mock import MagicMock, patch
from datetime import date
from service import app
from service.models import Recommendation, RecommendationType, db, init_db
from service.common import status  # HTTP Status Codes
from tests.factories import RecommendationFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/recommendations"
POP_REC_URL = "/recommendations/popular"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceServer(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        self.client = app.test_client()
        db.session.query(Recommendation).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def _create_recommendations(self, count):
        """Factory method to create recommendations in bulk"""
        recommendations = []
        for _ in range(count):
            test_recommendation = RecommendationFactory()
            response = self.client.post(BASE_URL, json=test_recommendation.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test recommendation",
            )
            new_recommendation = response.get_json()
            test_recommendation.id = new_recommendation["id"]
            recommendations.append(test_recommendation)
        return recommendations

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_recommendation(self):
        """It should Create a new Recommendation"""
        test_recommendation = RecommendationFactory()
        logging.debug("Test Recommendation: %s", test_recommendation.serialize())
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_recommendation = response.get_json()
        self.assertEqual(new_recommendation["user_id"], test_recommendation.user_id)
        self.assertEqual(
            new_recommendation["product_id"], test_recommendation.product_id
        )
        self.assertEqual(
            new_recommendation["bought_in_last_30_days"],
            test_recommendation.bought_in_last_30_days,
        )
        self.assertEqual(
            new_recommendation["recommendation_type"],
            test_recommendation.recommendation_type.name,
        )
        self.assertEqual(
            date.fromisoformat(new_recommendation["create_date"]), date.today()
        )
        self.assertEqual(
            date.fromisoformat(new_recommendation["update_date"]), date.today()
        )

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_recommendation = response.get_json()
        self.assertEqual(new_recommendation["user_id"], test_recommendation.user_id)
        self.assertEqual(
            new_recommendation["product_id"], test_recommendation.product_id
        )
        self.assertEqual(
            new_recommendation["recommendation_type"],
            test_recommendation.recommendation_type.name,
        )
        self.assertEqual(
            new_recommendation["bought_in_last_30_days"],
            test_recommendation.bought_in_last_30_days,
        )

    def test_create_recommendation_no_content_type(self):
        """It should not Create a Recommendation with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_recommendation_wrong_content_type(self):
        """It should not Create a Recommendation with the wrong content type"""
        response = self.client.post(BASE_URL, data="hello", content_type="text/html")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_recommendation_no_data(self):
        """It should not Create a Recommendation with missing data"""
        response = self.client.post(BASE_URL, content_type="application/json", json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_recommendation_wrong_user_id(self):
        """It should not Create a Recommendation with wrong user id"""
        test_recommendation = RecommendationFactory()
        logging.debug(test_recommendation)
        # change user id to string
        test_recommendation.user_id = "1"
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_recommendation_wrong_data(self):
        """It should not Create a Recommendation with wrong data"""
        response = self.client.post(BASE_URL, json={"foo": "bar"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    ######################################################################
    #  UPDATE   TEST   CASES
    ######################################################################

    def test_update_recommendation(self):
        """It should Update an existing Recommendation with value"""
        # create a recommendation to update
        test_reco = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_reco.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the recommendation
        new_reco = response.get_json()
        logging.debug(new_reco)
        new_reco["recommendation_type"] = RecommendationType.RECOMMENDED_FOR_YOU.name
        new_reco["rating"] = 4
        response = self.client.put(f"{BASE_URL}/{new_reco['id']}", json=new_reco)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_reco = response.get_json()
        self.assertEqual(
            updated_reco["recommendation_type"],
            RecommendationType.RECOMMENDED_FOR_YOU.name,
        )
        self.assertEqual(updated_reco["rating"], 4)
        self.assertEqual(updated_reco["update_date"], date.today().strftime("%Y-%m-%d"))
   
    def test_update_recommendation_with_wrong_rating_value(self):
        """It should respond with a 400 for rating that is not in range 1-5"""
        test_reco = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_reco.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recommendation_id = response.get_json()[
            "id"
        ]  # replace with actual recommendation id
        invalid_data = {
            "user_id": 1,
            "product_id": 2,
            "recommendation_type": "RECOMMENDED_FOR_YOU",  # replace with actual enum string
            "bought_in_last_30_days": False,
            "rating": 6,  # invalid rating value
        }
        response = self.client.put(
            f"/recommendations/{recommendation_id}",
            json=invalid_data,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("recommendation with rating", response.get_json()["message"])

    def test_update_recommendation_no_rating(self):
        """It should update a recommendation even with no rating in request body"""
        test_recommendation = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recommendation_id = response.get_json()[
            "id"
        ]
        previous_rating = response.get_json()[
            "rating"
        ]

        request_data = {
            "user_id": 1,
            "product_id": 4,
            "recommendation_type": "RECOMMENDED_FOR_YOU",  # replace with actual enum string
            "bought_in_last_30_days": False
        }
        response = self.client.put(f"/recommendations/{recommendation_id}", json=request_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_recommendation = response.get_json()
        self.assertEqual(updated_recommendation["rating"], previous_rating)

    def test_update_recommendation_with_non_integer_id(self):
        """It should respond with a 404 for non-integer ids"""
        response = self.client.put(BASE_URL + "/" + "abc", json={})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_recommendation_not_found(self):
        """
        Test case for when a recommendation with the provided ID is not found.
        """
        response = self.client.put(
            BASE_URL + "/" + str(999999),
            json={},
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    ######################################################################
    #  UPDATE A RECOMMENDATION RATING
    ######################################################################
    def test_update_recommendation_rating(self):
        """It should try to update the rating of an existing Recommendation"""
        # Create a recommendation with a rating
        test_reco = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_reco.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Update the rating of the recommendation
        recommendation_id = response.get_json()["id"]
        updated_rating = 5
        response = self.client.put(f"{BASE_URL}/{recommendation_id}/rating", json={"rating": updated_rating})
        
        # Verify the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_reco = response.get_json()
        self.assertEqual(updated_reco["rating"], updated_rating)
    
    def test_update_rating_for_nonexisting_recommendation_id(self):
        """It should respond with a 404 for no recommendation ID available"""
        recommendation_id = 99
        invalid_rating = 6
        response = self.client.put(f"{BASE_URL}/{recommendation_id}/rating", json={"rating": invalid_rating})

        # Verify the response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(f"Recommendation with id '{recommendation_id}' was not found.", response.get_json()["message"])

    def test_update_rating_with_non_integer_values(self):
        """It should respond with a 400 for non-integer ratings"""
        test_reco = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_reco.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recommendation_id = response.get_json()["id"]
        response = self.client.put(f"{BASE_URL}/{recommendation_id}/rating", json={"rating": "abc"})

        # Verify the response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Rating must be an integer between 0 and 5 (inclusive).", response.get_json()["message"])

    def test_update_rating_with_wrong_values(self):
        """It should respond with a 400 for ratings beyond range"""
        test_reco = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_reco.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recommendation_id = response.get_json()["id"]
        response = self.client.put(f"{BASE_URL}/{recommendation_id}/rating", json={"rating": 10})

        # Verify the response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Rating must be an integer between 0 and 5 (inclusive).", response.get_json()["message"])

    ######################################################################
    #  DELETE A RECOMMENDATION (READ)
    ######################################################################
    def test_delete_recommendation(self):
        """It should Delete a Recommendation"""
        test_recommendation = self._create_recommendations(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # makes sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  RETRIEVE/GET A RECOMMENDATION (READ)
    ######################################################################

    def test_get_recommendation(self):
        """It should Get a single recommendation"""
        # get the id of a recommendation
        test_recommendation = self._create_recommendations(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["user_id"], test_recommendation.user_id)

    def test_get_recommendation_not_found(self):
        """It should not Get a recommendation thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    ######################################################################
    #  LIST A RECOMMENDATION (LIST)
    ######################################################################
    def test_get_recommendation_list(self):
        """It should Get a list of Recommendations"""
        self._create_recommendations(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_query_recommendation_list_by_product_id(self):
        """It should Query Recommendations by Product ID"""
        recommendations = self._create_recommendations(10)
        test_product_id = recommendations[0].product_id
        product_id_recommendations = [
            recommendation
            for recommendation in recommendations
            if recommendation.product_id == test_product_id
        ]
        response = self.client.get(
            BASE_URL, query_string=f"product_id={test_product_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(product_id_recommendations))
        # check the data just to be sure
        for recommendation in data:
            self.assertEqual(recommendation["product_id"], test_product_id)

    def test_query_recommendation_list_by_user_id(self):
        """It should Query Recommendations by User ID"""
        recommendations = self._create_recommendations(10)
        test_user_id = recommendations[0].user_id
        user_id_recommendations = [
            recommendation
            for recommendation in recommendations
            if recommendation.user_id == test_user_id
        ]
        response = self.client.get(BASE_URL, query_string=f"user_id={test_user_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(user_id_recommendations))
        # check the data just to be sure
        for recommendation in data:
            self.assertEqual(recommendation["user_id"], test_user_id)

    def test_query_recommendation_list_by_bought_in_last30d(self):
        """It should Query Recommendations by bought in the last 30 days"""
        recommendations = self._create_recommendations(10)
        test_bought_in_last_30d = recommendations[0].bought_in_last_30_days
        bought_in_last_30d_recommendations = [
            recommendation
            for recommendation in recommendations
            if recommendation.bought_in_last_30_days == test_bought_in_last_30d
        ]
        response = self.client.get(
            BASE_URL, query_string=f"bought_in_last_30d={test_bought_in_last_30d}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(bought_in_last_30d_recommendations))
        # check the data just to be sure
        for recommendation in data:
            self.assertEqual(
                recommendation["bought_in_last_30_days"], test_bought_in_last_30d
            )

    # def test_update_rating_with_no_value(self):
    #     """It should respond with a 400 for trying to update rating with no value"""
    #     test_recommendation = RecommendationFactory()
    #     response = self.client.post(BASE_URL, json=test_recommendation.serialize())
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     recommendation_id = response.get_json()["id"]
    #     previous_rating = response.get_json()["rating"]

    #     request_data = {
    #         "user_id": 1,
    #         "product_id": 4,
    #         "recommendation_type": "RECOMMENDED_FOR_YOU",  # replace with actual enum string
    #         "bought_in_last_30_days": False
    #     }
    #     response = self.client.put(f"/recommendations/{recommendation_id}", json=request_data)

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     updated_recommendation = response.get_json()
    #     self.assertEqual(updated_recommendation["rating"], previous_rating)