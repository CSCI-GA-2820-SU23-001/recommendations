"""
Models for Recommendation

All of the models are stored in this module
"""
import logging
from datetime import date
from enum import Enum
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class RecommendationType(Enum):
    """Enumeration of valid Recommendation Types"""
    UPSELL = 0
    CROSS_SELL = 1
    FREQ_BOUGHT_TOGETHER = 2
    RECOMMENDED_FOR_YOU =3
    TRENDING = 4
    UNKOWN = 5

# Function to initialize the database
def init_db(app):
    """ Initializes the SQLAlchemy app """
    Recommendation.init_db(app)


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """


class Recommendation(db.Model):
    """
    Class that represents a Recommendation
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    create_date= db.Column(db.Date(), nullable=False, default=date.today())
    update_date= db.Column(db.Date(), nullable=False, default=date.today())
    bought_in_last_30_days = db.Column(db.Boolean, nullable=False, default=False)

    recommendation_type = db.Column(
        db.Enum(RecommendationType), nullable=False, server_default=(RecommendationType.UNKOWN.name)
    )

    def __repr__(self):
        return f"<Recommendation id=[{self.id}]>"

    def create(self):
        """
        Creates a Recommendation to the database
        """
        logger.info("Creating recommendation for user id %s", self.user_id)
        self.id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Recommendation to the database
        """
        logger.info("Saving %s", self.user_id)
        db.session.commit()

    def delete(self):
        """ Removes a Recommendation from the data store """
        logger.info("Deleting %s", self.user_id)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Recommendation into a dictionary """
        return {
            "id": self.id, 
            "user_id": self.user_id,
            "product_id": self.product_id,
            "recommendation_type": self.recommendation_type.name, # create string from enum
            "create_date": self.create_date.isoformat(),
            "update_date": self.update_date.isoformat(),
            "bought_in_last_30_days": self.bought_in_last_30_days,
            }

    def deserialize(self, data):
        """
        Deserializes a Recommendation from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.user_id = data["user_id"]
            self.product_id = data["product_id"]
            self.recommendation_type = getattr(RecommendationType, data["recommendation_type"]) # create enum from string
            self.create_date = date.fromisoformat(data["create_date"])
            self.update_date = date.fromisoformat(data["update_date"])
            self.bought_in_last_30_days = data["bought_in_last_30_days"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid Recommendation: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Recommendation: body of request contained bad or no data - "
                "Error message: " + str(error)
            ) from error
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Recommendations in the database """
        logger.info("Processing all Recommendations")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a Recommendation by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_userid(cls, userId):
        """Returns all Recommendations with the given user id

        Args:
            user_id (int): the user_id of the Recommendations you want to match
        """
        logger.info("Processing user_id query for %s ...", userId)
        return cls.query.filter(cls.user_id == userId)
