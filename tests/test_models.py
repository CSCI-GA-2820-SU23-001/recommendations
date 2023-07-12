"""
Test cases for Recommendation Model

"""
import os
import logging
import unittest
from datetime import date
from service.models import Recommendation, RecommendationType, DataValidationError, db
from service import app
from tests.factories import RecommendationFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  Recommendation   M O D E L   T E S T   C A S E S
######################################################################
class TestRecommendation(unittest.TestCase):
    """Test Cases for Recommendation Model"""

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
        self.assertEqual(
            data["recommendation_type"], recommendation.recommendation_type.name
        )
        self.assertIn("bought_in_last_30_days", data)
        self.assertEqual(
            data["bought_in_last_30_days"], recommendation.bought_in_last_30_days
        )
        self.assertIn("rating", data)
        self.assertEqual(data["rating"], recommendation.rating)
        self.assertEqual(
            date.fromisoformat(data["create_date"]), recommendation.create_date
        )
        self.assertEqual(
            date.fromisoformat(data["update_date"]), recommendation.update_date
        )

    def test_deserialize_a_recommendation(self):
        """It should de-serialize a Recommendation"""
        data = RecommendationFactory().serialize()
        recommendation = Recommendation()
        recommendation.deserialize(data)
        self.assertNotEqual(recommendation, None)
        self.assertEqual(recommendation.id, None)
        self.assertEqual(recommendation.user_id, data["user_id"])
        self.assertEqual(recommendation.product_id, data["product_id"])
        self.assertEqual(
            recommendation.bought_in_last_30_days, data["bought_in_last_30_days"]
        )
        self.assertEqual(recommendation.rating, data["rating"])
        self.assertEqual(recommendation.create_date, None)
        self.assertEqual(recommendation.update_date, None)

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

    def test_deserialize_wrong_user_id_data_type(self):
        """It should not de-serialize a Recommendation with wrong user_id data type"""
        data = RecommendationFactory().serialize()
        data["user_id"] = str(data["user_id"])
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_wrong_product_id_data_type(self):
        """It should not de-serialize a Recommendation with wrong product_id data type"""
        data = RecommendationFactory().serialize()
        data["product_id"] = str(data["product_id"])
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_wrong_bought_in_last_30_days_data_type(self):
        """It should not de-serialize a Recommendation with wrong bought_in_last_30_days data type"""
        data = RecommendationFactory().serialize()
        data["bought_in_last_30_days"] = "True"
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_wrong_recommendation_type_data_type(self):
        """It should not de-serialize a Recommendation with wrong recommendation_type data type"""
        data = RecommendationFactory().serialize()
        data["recommendation_type"] = 2
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_wrong_rating_data_type(self):
        """It should not de-serialize a Recommendation with wrong rating data type"""
        data = RecommendationFactory().serialize()
        data["rating"] = str(data["rating"])
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_create_a_recommendation(self):
        """It should Create a recommendation and assert that it exists"""
        recommendation = Recommendation(
            user_id=1,
            product_id=2,
            bought_in_last_30_days=True,
            recommendation_type=RecommendationType.UPSELL.name,
        )
        self.assertEqual(str(recommendation), "<Recommendation id=[None]>")
        self.assertTrue(recommendation is not None)
        self.assertEqual(recommendation.id, None)
        self.assertEqual(recommendation.user_id, 1)
        self.assertEqual(recommendation.product_id, 2)
        self.assertEqual(recommendation.bought_in_last_30_days, True)
        self.assertEqual(
            recommendation.recommendation_type, RecommendationType.UPSELL.name
        )
        recommendation = Recommendation(
            user_id=1,
            product_id=2,
            bought_in_last_30_days=False,
            recommendation_type=RecommendationType.UPSELL.name,
        )
        self.assertEqual(recommendation.bought_in_last_30_days, False)

    def test_add_a_recommendation(self):
        """It should Create a recommendation and add it to the database"""
        recommendations = Recommendation.all()
        self.assertEqual(recommendations, [])
        recommendation = Recommendation(
            user_id=1,
            product_id=2,
            bought_in_last_30_days=True,
            recommendation_type=RecommendationType.UPSELL.name,
        )
        self.assertTrue(recommendation is not None)
        self.assertEqual(recommendation.id, None)
        recommendation.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(recommendation.id)
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 1)

    def test_update_recommendation(self):
        """Test if a recommendation can be updated in the database"""
        reco = RecommendationFactory()
        reco.update_date = date.today()
        logging.debug(reco)
        reco.id = None
        reco.create()
        logging.debug(reco)
        self.assertIsNotNone(reco.id)
        # Change it and save it
        reco.recommendation_type = RecommendationType.RECOMMENDED_FOR_YOU
        original_id = reco.id
        reco.update()
        self.assertEqual(reco.id, original_id)
        self.assertEqual(
            reco.recommendation_type, RecommendationType.RECOMMENDED_FOR_YOU
        )
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        recos = Recommendation.all()
        self.assertEqual(len(recos), 1)
        self.assertEqual(recos[0].id, original_id)
        self.assertEqual(
            recos[0].recommendation_type, RecommendationType.RECOMMENDED_FOR_YOU
        )
        self.assertEqual(recos[0].update_date, date.today())
        self.assertEqual(recos[0].rating, reco.rating)

    def test_delete_a_recommendation(self):
        """It should Delete a Recommendation"""
        test_recommendation = RecommendationFactory()
        test_recommendation.create()
        self.assertEqual(len(Recommendation.all()), 1)

        # delete the recommendation and make sure it isn't in the database
        test_recommendation.delete()
        self.assertEqual(len(Recommendation.all()), 0)
