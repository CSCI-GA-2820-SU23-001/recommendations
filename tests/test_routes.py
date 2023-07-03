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
POP_REC_URL = "/recommendations/popular"
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
    
    def _create_recommendations(self, count):
        """Factory method to create recommendations in bulk"""
        recommendations = []
        for _ in range(count):
            test_recommendation = RecommendationFactory()
            response = self.client.post(BASE_URL, json=test_recommendation.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test recommendation"
            )
            new_recommendation = response.get_json()
            test_recommendation.id = new_recommendation["id"]
            recommendations.append(test_recommendation)
        return recommendations

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

    # def test_update_recommendation(self):
    #     """It should Update an existing Recommendation"""
    #     recommendation = Recommendation(
    #         user_id=1, 
    #         product_id=2, 
    #         bought_in_last_30_days=True, 
    #         recommendation_type=RecommendationType.UPSELL.name
    #     )
    #     db.session.add(recommendation)
    #     db.session.commit()

    #     current_recommendation = Recommendation.query.get(recommendation.id)
    #     current_type = current_recommendation.recommendation_type
       
    #     response = self.client.put(BASE_URL + '/' +str(recommendation.id), json={})
    #     # print(response)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    #     updated_recommendation = response.get_json()
    #     self.assertNotEqual(updated_recommendation["recommendation_type"], current_type.name)
    #     self.assertEqual(date.fromisoformat(updated_recommendation["update_date"]), date.today())

    # def test_update_recommendation(self):
    #     """ Test updating a recommendation """
    #     recommendation = Recommendation(user_id=1, product_id=2, bought_in_last_30_days=True,
    #                                     recommendation_type=RecommendationType.UPSELL.name)
    #     recommendation.create()
    #     recommendation_id = recommendation.id

    #     # Define a new type
    #     new_type = RecommendationType.CROSS_SELL.name

    #     # Send PUT request with new type
    #     response = self.client.put(
    #         "/recommendations/{}".format(recommendation_id),
    #         json={"recommendation_type": new_type},
    #         content_type="application/json",
    #     )

    #     # Check the status code and the returned JSON
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     new_json = response.get_json()
    #     self.assertEqual(new_json["recommendation_type"], new_type)

    #     # Verify that the change was made in the database
    #     updated_recommendation = Recommendation.query.get(recommendation_id)
    #     self.assertEqual(updated_recommendation.recommendation_type.name, new_type)
    def test_update_recommendation(self):
        """It should Update an existing Recommendation"""
        # create a recommendation to update
        test_reco = RecommendationFactory()
        test_reco.update_date=date.today()
        response = self.client.post(BASE_URL, json=test_reco.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the pet
        new_reco = response.get_json()
        logging.debug(new_reco)
        new_reco["recommendation_type"] = RecommendationType.RECOMMENDED_FOR_YOU.name
        response = self.client.put(f"{BASE_URL}/{new_reco['id']}", json=new_reco)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_reco = response.get_json()
        self.assertEqual(updated_reco["recommendation_type"], RecommendationType.RECOMMENDED_FOR_YOU.name)
        self.assertEqual(updated_reco["update_date"], date.today().strftime('%Y-%m-%d'))

    
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



    # TEST CASES FOR DELETE #

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

    def test_get_popular_recommendation_list(self):
        """It should Get a list of Popular Recommendations"""
        # Create test recommendations for 5 products
        count = 5
        # Test Logic:
        # Create 1 recommendation for 1st product, 2 for 2nd, ...
        # 5th product is most popular because of 5 recommendations
        for product in range(1, count + 1):
            for _ in range(1, product + 1):
                test_rec = RecommendationFactory().serialize()
                test_rec["product_id"] = 123 + product
                response = self.client.post(BASE_URL, json=test_rec)
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test error conditions first
        response = self.client.get(f"{POP_REC_URL}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(f"{POP_REC_URL}", query_string="count=more")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(f"{POP_REC_URL}", query_string="count=6")
        self.assertEqual(response.status_code, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        response = self.client.get(f"{POP_REC_URL}", query_string="count=0")
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

        # Test valid condition: Verify response length and most popular recommendation
        response = self.client.get(f"{POP_REC_URL}", query_string="count=2")
        data = response.get_json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["product_id"], 128)

    def test_query_recommendation_list_by_product_id(self):
        """It should Query Recommendations by Product ID"""
        recommendations = self._create_recommendations(10)
        test_product_id = recommendations[0].product_id
        product_id_recommendations = [
            recommendation for recommendation in recommendations
            if recommendation.product_id == test_product_id]
        response = self.client.get(
            BASE_URL,
            query_string=f"product_id={test_product_id}"
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
            recommendation for recommendation in recommendations
            if recommendation.user_id == test_user_id]
        response = self.client.get(
            BASE_URL,
            query_string=f"user_id={test_user_id}"
        )
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
            recommendation for recommendation in recommendations
            if recommendation.bought_in_last_30_days == test_bought_in_last_30d]
        response = self.client.get(
            BASE_URL,
            query_string=f"bought_in_last_30d={test_bought_in_last_30d}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(bought_in_last_30d_recommendations))
        # check the data just to be sure
        for recommendation in data:
            self.assertEqual(recommendation["bought_in_last_30_days"], test_bought_in_last_30d)
