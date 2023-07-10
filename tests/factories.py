"""
Test Factory to make fake objects for testing
"""

from datetime import date

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate
from service.models import Recommendation, RecommendationType


class RecommendationFactory(factory.Factory):
    """Creates fake recommendations that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Recommendation

    id = factory.Sequence(lambda n: n)
    user_id = FuzzyChoice(range(1, 10))
    product_id = FuzzyChoice(range(1, 50))
    create_date = FuzzyDate(date(2023, 1, 1))
    update_date = FuzzyDate(date(2023, 1, 1))
    bought_in_last_30_days = FuzzyChoice(choices=[True, False])
    recommendation_type = FuzzyChoice(choices=[RecommendationType.UPSELL, RecommendationType.CROSS_SELL,
                                               RecommendationType.FREQ_BOUGHT_TOGETHER, RecommendationType.RECOMMENDED_FOR_YOU,
                                               RecommendationType.TRENDING, RecommendationType.UNKNOWN])
    rating=FuzzyChoice(choices=[1,2,3,4,5])
    