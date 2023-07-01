"""
TestRecommendation API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from logging import Formatter
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import app
from service.models import Recommendation, RecommendationType, DataValidationError, db, init_db
from service.common import status  # HTTP Status Codes
from tests.factories import RecommendationFactory
from datetime import date


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/recommendations"

######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        self.client = app.test_client()
        db.session.query(Recommendation).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_recommendation(self):
        """It should Create a new Recommendation"""
        test_recommendation = RecommendationFactory()
        logging.debug("Test Recommendation: %s", test_recommendation.serialize())
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # TODO Make sure location header is set
        '''location = response.headers.get("Location", None)
        self.assertIsNotNone(location)'''

        # Check the data is correct
        new_recommendation = response.get_json()
        self.assertEqual(new_recommendation["user_id"], test_recommendation.user_id)
        self.assertEqual(new_recommendation["product_id"], test_recommendation.product_id)
        self.assertEqual(new_recommendation["bought_in_last_30_days"], test_recommendation.bought_in_last_30_days)
        self.assertEqual(new_recommendation["recommendation_type"], test_recommendation.recommendation_type.name)
        self.assertEqual(date.fromisoformat(new_recommendation["create_date"]), test_recommendation.create_date)
        self.assertEqual(date.fromisoformat(new_recommendation["update_date"]), test_recommendation.update_date)


        # TODO Check that the location header was correct

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

 ######################################################################
    #  UPDATE   TEST   CASES
#######################################################################

    def test_update_recommendation(self):
        """It should Update an existing Recommendation"""
        recommendation = Recommendation(
            user_id=1, 
            product_id=2, 
            bought_in_last_30_days=True, 
            recommendation_type=RecommendationType.UPSELL.name
        )
        db.session.add(recommendation)
        db.session.commit()

        current_recommendation = Recommendation.query.get(recommendation.id)
        current_type = current_recommendation.recommendation_type
       
        response = self.client.put(BASE_URL + '/' +str(recommendation.id), json={})
        # print(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_recommendation = response.get_json()
        self.assertNotEqual(updated_recommendation["recommendation_type"], current_type.name)
        self.assertEqual(date.fromisoformat(updated_recommendation["update_date"]), date.today())
    def test_method_not_allowed(self):
        """It should return 405 when an unsupported method is used"""
        recommendation = Recommendation(
            user_id=1, 
            product_id=2, 
            bought_in_last_30_days=True, 
            recommendation_type=RecommendationType.UPSELL.name
        )
        db.session.add(recommendation)
        db.session.commit()

        # Make a GET request to the update_recommendations route
        response = self.client.get(BASE_URL + '/'+ str(recommendation.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        data = response.get_json()
        self.assertEqual(data["error"], "Method not Allowed")
    
    def test_update_recommendation_with_non_integer_id(self):
        """It should respond with a 404 for non-integer ids"""
        response = self.client.put(BASE_URL + '/' +"abc", json={})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_recommendation_not_found(self):
        """
        Test case for when a recommendation with the provided ID is not found.
        """
        response = self.client.put(BASE_URL + '/'+ str(999999), json={}, headers={"Content-Type": "application/json"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

