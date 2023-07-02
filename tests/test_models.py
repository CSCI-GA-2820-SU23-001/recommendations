"""
Test cases for Recommendation Model

"""
import os
import logging
import unittest
from service.models import Recommendation, RecommendationType, DataValidationError, db
from service import app
from tests.factories import RecommendationFactory
from random import choice
from datetime import date
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  Recommendation   M O D E L   T E S T   C A S E S
######################################################################
class TestRecommendation(unittest.TestCase):
    """ Test Cases for Recommendation Model """

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Recommendation.init_db(app)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        """This runs before each test"""
        db.drop_all()
        db.create_all()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_example_replace_this(self):
        """ It should always be true """
        self.assertTrue(True)
    
    def test_serialize_a_recommendation(self):
        """It should serialize a Recommendation"""
        recommendation = RecommendationFactory()
        data = recommendation.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], recommendation.id)
        self.assertIn("user_id", data)
        self.assertEqual(data["user_id"], recommendation.user_id)
        self.assertIn("product_id", data)
        self.assertEqual(data["product_id"], recommendation.product_id)
        self.assertIn("recommendation_type", data)
        self.assertEqual(data["recommendation_type"], recommendation.recommendation_type.name)
        self.assertIn("bought_in_last_30_days", data)
        self.assertEqual(data["bought_in_last_30_days"], recommendation.bought_in_last_30_days)
        self.assertEqual(date.fromisoformat(data["create_date"]), recommendation.create_date)
        self.assertEqual(date.fromisoformat(data["update_date"]), recommendation.update_date)

    def test_deserialize_a_recommendation(self):
        """It should de-serialize a Recommendation"""
        data = RecommendationFactory().serialize()
        recommendation = Recommendation()
        recommendation.deserialize(data)
        self.assertNotEqual(recommendation, None)
        self.assertEqual(recommendation.id, None)
        self.assertEqual(recommendation.user_id, data["user_id"])
        self.assertEqual(recommendation.product_id, data["product_id"])
        self.assertEqual(recommendation.bought_in_last_30_days, data["bought_in_last_30_days"])
        self.assertEqual(recommendation.create_date, date.fromisoformat(data["create_date"]))
        self.assertEqual(recommendation.update_date, date.fromisoformat(data["update_date"]))

    def test_deserialize_missing_data(self):
        """It should not deserialize a Recommendation with missing data"""
        data = {"id": 1, "user_id": 2, "product_id": 3}
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_create_a_recommendation(self):
        """It should Create a recommendation and assert that it exists"""
        recommendation = Recommendation(user_id=1, product_id=2, bought_in_last_30_days=True, 
                                        recommendation_type=RecommendationType.UPSELL.name)
        self.assertEqual(str(recommendation), "<Recommendation id=[None]>")
        self.assertTrue(recommendation is not None)
        self.assertEqual(recommendation.id, None)
        self.assertEqual(recommendation.user_id, 1)
        self.assertEqual(recommendation.product_id, 2)
        self.assertEqual(recommendation.bought_in_last_30_days, True)
        self.assertEqual(recommendation.recommendation_type, RecommendationType.UPSELL.name)
        recommendation = Recommendation(user_id=1, product_id=2, bought_in_last_30_days=False, 
                                        recommendation_type=RecommendationType.UPSELL.name)
        self.assertEqual(recommendation.bought_in_last_30_days, False)

    def test_add_a_recommendation(self):
        """It should Create a recommendation and add it to the database"""
        recommendations = Recommendation.all()
        self.assertEqual(recommendations, [])
        recommendation = Recommendation(user_id=1, product_id=2, bought_in_last_30_days=True, 
                                        recommendation_type=RecommendationType.UPSELL.name)
        self.assertTrue(recommendation is not None)
        self.assertEqual(recommendation.id, None)
        recommendation.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(recommendation.id)
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 1)

    # def test_update_a_recommendation(self):
    #     """It should Update a recommendation in the database"""
    #     recommendation = Recommendation(user_id=1, product_id=2, bought_in_last_30_days=True,
    #                                     recommendation_type=RecommendationType.UPSELL.name)
    #     recommendation.create()

    #     # Assert that it was assigned an id and shows up in the database
    #     self.assertIsNotNone(recommendation.id)

    #     original_id = recommendation.id
    #     original_type = recommendation.recommendation_type

    #     # Define the possible recommendation types
    #     possible_types = [RecommendationType.UPSELL, RecommendationType.CROSS_SELL,
    #                     RecommendationType.FREQ_BOUGHT_TOGETHER, RecommendationType.RECOMMENDED_FOR_YOU, RecommendationType.TRENDING]

    #     # Remove the current type from the possible types
    #     possible_types.remove(original_type)

    #     # Randomly select a new type
    #     new_type = choice(possible_types)

    #     # Update the recommendation
    #     recommendation.recommendation_type = new_type
    #     recommendation.update()

    #     updated_recommendation = Recommendation.find(original_id)

    #     self.assertEqual(updated_recommendation.id, original_id)
    #     self.assertNotEqual(updated_recommendation.recommendation_type, original_type)
    #     self.assertEqual(updated_recommendation.recommendation_type, new_type)
    def test_update_recommendation(self):
        """Test if a recommendation can be updated in the database"""
        # Get the initial type
        recommendation=Recommendation(user_id=1, product_id=2, bought_in_last_30_days=True,
                                             recommendation_type=RecommendationType.UPSELL.name)
        recommendation.create()
        old_type = recommendation.recommendation_type

        # Define a new type
        new_type = RecommendationType.CROSS_SELL.name

        # Update the recommendation and commit to the database
        recommendation.recommendation_type = new_type
        db.session.commit()

        # Get the updated recommendation
        recommendation = Recommendation.query.get(recommendation.id)

        # Assert the recommendation type has been updated
        self.assertNotEqual(recommendation.recommendation_type.name, old_type)
        self.assertEqual(recommendation.recommendation_type.name, new_type)


    def test_delete_a_recommendation(self):
        """It should Delete a Recommendation"""
        test_recommendation = RecommendationFactory()
        test_recommendation.create()
        self.assertEqual(len(Recommendation.all()), 1)
        
        # delete the recommendation and make sure it isn't in the database
        test_recommendation.delete()
        self.assertEqual(len(Recommendation.all()), 0)




    
        

