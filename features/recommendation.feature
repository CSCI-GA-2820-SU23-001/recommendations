Feature: The recommendation service back-end
    As a E-Commerce owner
    I need a RESTful recommendation service
    So that I can keep track of all the recommendation made to the customer

    Background:
        Given the following recommendation
            | id | user_id | product_id | bought_in_last_30_days | rating | recommendation_type |
            | 1  | 11      | 15         | True                   | 2      | UPSELL              |
            | 2  | 21      | 10         | True                   | 3      | CROSS_SELL          |
            | 3  | 1       | 28         | False                  | 4      | TRENDING            |
            | 4  | 5       | 31         | False                  | 0      | UPSELL              |
            | 5  | 9       | 16         | False                  | 1      | TRENDING            |


    Scenario: The server is running
        When I visit the "home page"
        Then I should see "Recommendation RESTful Service" in the title
        And I should not see "404 Not Found"

    Scenario: Create a Recommendation
        When I visit the "home page"
        And I set the "User ID" to "11"
        And I set the "Product ID" to "16"
        And I select "True" in the "Bought in last 30 days"
        And I select "Recommended For You" in the "Recommendation Type"
        And I press the "Create" button
        Then I should see the message "Success"
        When I copy the "ID" field
        And I press the "Clear" button
        Then the "ID" field should be empty
        And the "User ID" field should be empty
        And the "Product ID" field should be empty
        And the "Bought in last 30 days" field should be empty
        And the "Recommendation Type" field should be empty
        # When I copy the "ID" field
        When I paste the "ID" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "11" in the "User ID" field
        And I should see "16" in the "Product ID" field
        And I should see "True" in the "Bought in last 30 days"
        And I should see "Recommended For You" in the "Recommendation Type"

    Scenario: Update a Recommendation
        When I visit the "home page"
        And I set the "User ID" to "21"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "21" in the "User ID" field
        And I should see "10" in the "Product ID" field
        And I should see "Cross Sell" in the "Recommendation Type" dropdown
        And I should see "CROSS_SELL" in the results
        When I select "Recommended For You" in the "Recommendation Type" dropdown
        And I press the "Update" button
        Then I should see the message "Success"
        When I copy the "Id" field
        And I press the "Clear" button
        And I paste the "Id" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "Recommended For You" in the "Recommendation Type" dropdown
        And I should not see "Cross Sell" in the "Recommendation Type" dropdown
        When I press the "Clear" button
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "RECOMMENDED_FOR_YOU" in the results
        And I should not see "CROSS_SELL" in the results

    Scenario: List all Recommendations
        When I visit the "home page"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "11" in the "USER ID" field
        And I should see "15" in the "PRODUCT ID" field
        And I should see "CROSS_SELL" in the results
        And I should see "TRENDING" in the results
        And I should see "UPSELL" in the results
        And I should not see "RECOMMENDED_FOR_YOU" in the results

    Scenario: Query a Recommendation
        When I visit the "home page"
        And I set the "USER ID" to "5"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "UPSELL" in the results
        And I should see "Up Sell" in the "Recommendation Type" dropdown
        And I should see "31" in the results
        And I should see "31" in the "PRODUCT ID" field
        And I should see "False" in the "Bought in last 30 days" dropdown
        And I should not see "TRENDING" in the results
        And I should not see "CROSS_SELL" in the results
    

    Scenario: Delete a Recommendation
        When I visit the "home page"
        And I set the "User ID" to "21"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "CROSS_SELL" in the results
        And I should see "21" in the "USER ID" field
        When I copy the "ID" field
        And I press the "Clear" button
        And I paste the "ID" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        When I press the "Delete" button
        Then I should see the message "Recommendation has been Deleted!"
        When I paste the "ID" field
        And I press the "Retrieve" button
        Then I should see the message "not found"
        When I press the "Clear" button
        And I press the "Search" button
        Then I should see the message "Success"
        And I should not see "CROSS_SELL" in the results

    Scenario: Rate a Recommendation
        When I visit the "home page"
        And I set the "User ID" to "21"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "21" in the "User ID" field
        And I should see "10" in the "Product ID" field
        And I should see "3" in the "Rating" dropdown
        When I select "4" in the "Rating" dropdown
        And I press the "Rate" button
        Then I should see the message "Success"
        When I copy the "Id" field
        And I press the "Clear" button
        And I paste the "Id" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "21" in the "User ID" field
        And I should see "10" in the "Product ID" field
        And I should see "4" in the "Rating" dropdown
        When I press the "Clear" button
        And I set the "User ID" to "21"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "21" in the "User ID" field
        And I should see "10" in the "Product ID" field
        And I should see "4" in the "Rating" dropdown
        And I should see "4" in the results