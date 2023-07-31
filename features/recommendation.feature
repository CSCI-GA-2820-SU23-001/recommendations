Feature: The recommendation service back-end
    As a E-Commerce owner
    I need a RESTful recommendation service
    So that I can keep track of all the recommendation made to the customer

    Background:
        Given the following recommendation
            | id | user_id | product_id | bought_in_last_30_days | rating | recommendation_type |
            | 1  | 11      | 15         | True                   | 2      | UPSELL              |
            | 2  | 21      | 10         | True                   | 3      | CROSS_SELL          |
            | 3  | 1       | 21         | False                  | 4      | TRENDING            |
            | 4  | 5       | 1          | False                  | 0      | UPSELL              |
            | 5  | 11      | 1          | False                  | 1      | TRENDING            |


    Scenario: The server is running
        When I visit the "home page"
        Then I should see "Recommendation RESTful Service" in the title
        And I should not see "404 Not Found"

    Scenario: Create a Recommendation
        When I visit the "home page"
        And I set the "User ID" to "2"
        And I set the "Product ID" to "21"
        And I select "True" in the "Bought in last 30 days"
        And I select "Up Sell" in the "Recommendation Type"
        And I press the "Create" button
        Then I should see the message "Success"
        When I press the "Clear" button
        Then the "User ID" field should be empty
        And the "Product ID" field should be empty
        And the "Bought in last 30 days" field should be empty
        And the "Recommendation Type" field should be empty
        When I copy the "ID" field
        And I paste the "ID" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "2" in the "User ID" field
        And I should see "21" in the "Product ID" field
        And I should see "True" in the "Bought in last 30 days"
        And I should see "Up Sell" in the "Recommendation Type"

    Scenario: Update a Recommendation
        When I visit the "home page"
        And I set the "User ID" to "21"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "21" in the "User ID" field
        And I should see "10" in the "Product ID" field
        When I change "User ID" to "30"
        And I press the "Update" button
        Then I should see the message "Success"
        When I copy the "Id" field
        And I press the "Clear" button
        And I paste the "Id" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "30" in the "User ID" field
        When I press the "Clear" button
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "30" in the results
        And I should not see "21" in the results

    Scenario: List all pets
        When I visit the "home page"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "11" in the "USER ID" field
        And I should see "15" in the "PRODUCT ID" field
    

    Scenario: Delete a Recommendation
        When I visit the "home page"
        And I set the "Product ID" to "15"
        And I press the "Search" button
        Then I should see the message "Success"
        When I copy the "ID" field
        And I press the "Clear" button
        And I paste the "ID" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        When I press the "Delete" button
        Then I should see the message "Recommendation has been Deleted!"
        When I press the "Clear" button
        And I press the "Search" button
        Then I should see the message "Success"
        And I should not see "15" in the results