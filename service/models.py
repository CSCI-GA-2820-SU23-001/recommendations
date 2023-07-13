"""
Models for Recommendation

All of the models are stored in this module
"""
import logging
from datetime import date
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class RecommendationType(Enum):
    """Enumeration of valid Recommendation Types"""

    UPSELL = 0
    CROSS_SELL = 1
    FREQ_BOUGHT_TOGETHER = 2
    RECOMMENDED_FOR_YOU = 3
    TRENDING = 4
    UNKNOWN = 5


# Function to initialize the database
def init_db(app):
    """Initializes the SQLAlchemy app"""
    Recommendation.init_db(app)


def check_is_int(value, error_message):
    """Throws DataValidationError if the value is not an int"""
    if not isinstance(value, int):
        raise DataValidationError(error_message)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Recommendation(db.Model):
    """
    Class that represents a Recommendation
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    create_date = db.Column(db.Date(), nullable=False, default=date.today())
    update_date = db.Column(db.Date(), nullable=False, default=date.today())
    bought_in_last_30_days = db.Column(db.Boolean, nullable=False, default=False)
    rating = db.Column(
        db.Integer,
        CheckConstraint("rating>=0 AND rating<=5", name="rating_check"),
        nullable=False,
        default=0,
    )

    recommendation_type = db.Column(
        db.Enum(RecommendationType),
        nullable=False,
        server_default=(RecommendationType.UNKNOWN.name),
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
        """Removes a Recommendation from the data store"""
        logger.info("Deleting %s", self.id)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """Serializes a Recommendation into a dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "recommendation_type": self.recommendation_type.name,  # create string from enum
            "create_date": self.create_date.isoformat(),
            "update_date": self.update_date.isoformat(),
            "bought_in_last_30_days": self.bought_in_last_30_days,
            "rating": self.rating,
        }

    def deserialize(self, data):
        """
        Deserializes a Recommendation from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            check_is_int(data["user_id"], "Invalid type for int [user_id]")
            self.user_id = data["user_id"]
            check_is_int(data["product_id"], "Invalid type for int [product_id]")
            self.product_id = data["product_id"]
            if isinstance(data["recommendation_type"], str):
                self.recommendation_type = getattr(
                    RecommendationType, data["recommendation_type"]
                )  # create enum from string
            else:
                raise DataValidationError(
                    "Invalid type for string [recommendation_type]: "
                    + str(type(data["recommendation_type"]))
                )
            if isinstance(data["bought_in_last_30_days"], bool):
                self.bought_in_last_30_days = data["bought_in_last_30_days"]
            else:
                raise DataValidationError(
                    "Invalid type for bool [bought_in_last_30_days]: "
                    + str(type(data["bought_in_last_30_days"]))
                )
            if data.get("rating"):
                check_is_int(data["rating"], "Invalid type for int [rating]")
                self.rating = data["rating"]

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
        """Initializes the database session"""
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """Returns all of the Recommendations in the database"""
        logger.info("Processing all Recommendations")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Recommendation by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_user_id(cls, user_id):
        """Returns all Recommendations with the given user id

        Args:
            user_id (int): the user_id of the Recommendations you want to match
        """
        logger.info("Processing user_id query for %s ...", user_id)
        return cls.query.filter(cls.user_id == user_id)

    @classmethod
    def find_by_product_id(cls, by_id: int) -> list:
        """Returns all Recommendations for given Product ID"""
        logger.info("Processing lookup for product id %s ...", by_id)
        return cls.query.filter(cls.product_id == by_id)

    @classmethod
    def find_by_bought_in_last_30d(cls, bought_in_last_30d: bool = True) -> list:
        """Returns all Recommendations bought in last 30d"""
        logger.info(
            "Processing bought_in_last30d lookup for %s ...", bought_in_last_30d
        )
        return cls.query.filter(cls.bought_in_last_30_days == bought_in_last_30d)

    @classmethod
    def find_by_recommendation_type(
        cls, recommendation_type: RecommendationType = RecommendationType.UNKNOWN
    ) -> list:
        """Returns all Recommendations for given Type"""
        logger.info(
            "Processing lookup for recommendation type %s ...", recommendation_type
        )
        return cls.query.filter(cls.recommendation_type == recommendation_type)
