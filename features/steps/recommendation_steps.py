'''
Recommendation Steps

Steps file for Recommendation.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
'''

import requests
from behave import given

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204


@given('the following recommendation')
def step_impl(context):
    """ Delete all Recommendations and load new ones """

    # List all of the recommendations and delete them one by one
    rest_endpoint = f"{context.base_url}/api/recommendations"
    resp = requests.get(rest_endpoint)
    assert(resp.status_code == HTTP_200_OK)
    for recommendation in resp.json():
        resp = requests.delete(f"{rest_endpoint}/{recommendation['id']}")
        assert(resp.status_code == HTTP_204_NO_CONTENT)

    # load the database with new recommendations
    for row in context.table:
        payload = {
            "user_id" : int(row['user_id']),
            "product_id" : int(row['product_id']),
            "bought_in_last_30_days" : row['bought_in_last_30_days'] in ['True','true', True],
            "rating" : int(row['rating']),
            "recommendation_type" : row['recommendation_type'] 
        }
           
        context.resp = requests.post(rest_endpoint,json=payload)
        assert context.resp.status_code == HTTP_201_CREATED


