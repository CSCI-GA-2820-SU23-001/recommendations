"""
Models for Recommendation

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from datetime import date
from flask import Flask

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
    name = db.Column(db.String(63), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    create_date= db.Column(db.Date(), nullable=False, default=date.today())
    update_date= db.Column(db.Date(), nullable=False, default=date.today())
    
    recommendation_type = db.Column(
        db.Enum(RecommendationType), nullable=False, server_default=(RecommendationType.UNKOWN.name)
    )

    def __repr__(self):
        return f"<Recommendation {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Recommendation to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Recommendation to the database
        """
        logger.info("Saving %s", self.name)
        db.session.commit()

    def delete(self):
        """ Removes a Recommendation from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Recommendation into a dictionary """
        return {
            "id": self.id, 
            "name": self.name,
            "product_id": self.product_id,
            "recommendation_type": self.recommendation_type,
            "create_date": self.create_date,
            "update_date": self.update_date
            }

    def deserialize(self, data):
        """
        Deserializes a Recommendation from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.product_id = data["product_id"]
            self.recommendation_type = data["recommendation_type"]
            self.create_date = data["create_date"]
            self.update_date = data["update_date"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid Recommendation: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Recommendation: body of request contained bad or no data - "
                "Error message: " + error
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
    def find_by_name(cls, name):
        """Returns all Recommendations with the given name

        Args:
            name (string): the name of the Recommendations you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
