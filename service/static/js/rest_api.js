$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#reco_id").val(res.id.toString());
        $("#reco_user_id").val(res.user_id.toString());
        $("#reco_product_id").val(res.product_id);
        if (res.bought_in_last_30_days == true) {
            $("#reco_bought_in_last_30_days").val("true");
        } else {
            $("#reco_bought_in_last_30_days").val("false");
        }
        $("#reco_rating").val(res.rating.toString());
        $("#reco_recommendation_type").val(res.recommendation_type);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#reco_user_id").val("");
        $("#reco_product_id").val("");
        $("#reco_bought_in_last_30_days").val("");
        $("#reco_rating").val("");
        $("#reco_recommendation_type").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Recommendation
    // ****************************************

    $("#create-btn").click(function () {

        let user_id = $("#reco_user_id").val();
        let product_id = $("#reco_product_id").val();
        let recommendation_type = $("#reco_recommendation_type").val();
        let bought = $("#reco_bought_in_last_30_days").val() == "true";

        let data = {
            "user_id": parseInt(user_id),
            "product_id": parseInt(product_id),
            "recommendation_type": recommendation_type,
            "bought_in_last_30_days": bought
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: "/api/recommendations",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_form_data(res)
            console.log(res)
            console.log('hello')
            flash_message("Success")
        });

        ajax.fail(function (res) {
            console.log('FAIL')
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Update a Recommendation
    // ****************************************

    $("#update-btn").click(function () {

        let reco_id = $("#reco_id").val();
        let user_id = $("#reco_user_id").val();
        let product_id = $("#reco_product_id").val();
        let bought_in_last_30_days = $("#reco_bought_in_last_30_days").val() == "true";
        let recommendation_type = $("#reco_recommendation_type ").val();

        let data = {
            "user_id": parseInt(user_id),
            "product_id": parseInt(product_id),
            "bought_in_last_30_days": bought_in_last_30_days,
            "recommendation_type": recommendation_type,
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/recommendations/${reco_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Recommendation
    // ****************************************

    $("#retrieve-btn").click(function () {

        let reco_id = $("#reco_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/recommendations/${reco_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Recommendation
    // ****************************************

    $("#delete-btn").click(function () {

        let reco_id = $("#reco_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/recommendations/${reco_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function (res) {
            clear_form_data()
            flash_message("Recommendation has been Deleted!")
        });

        ajax.fail(function (res) {
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#reco_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for  Recommendations
    // ****************************************

    $("#search-btn").click(function () {

        let user_id = $("#reco_user_id").val();

        let queryString = ""

        if (user_id) {
            queryString += 'user_id=' + user_id
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/recommendations?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">User ID</th>'
            table += '<th class="col-md-2">Product ID</th>'
            table += '<th class="col-md-2">Create Date</th>'
            table += '<th class="col-md-2">Update Date</th>'
            table += '<th class="col-md-2">Bought in last 30 days</th>'
            table += '<th class="col-md-2">Rating</th>'
            table += '<th class="col-md-2">Recommendation Type</th>'
            table += '</tr></thead><tbody>'
            let firstRecommendation = "";
            for (let i = 0; i < res.length; i++) {
                let recommendation = res[i];
                table += `<tr id="row_${i}"><td>${recommendation.id}</td><td>${recommendation.user_id}</td><td>${recommendation.product_id}</td><td>${recommendation.create_date}</td><td>${recommendation.update_date}</td><td>${recommendation.bought_in_last_30_days}</td><td>${recommendation.rating}</td><td>${recommendation.recommendation_type}</td></tr>`;
                if (i == 0) {
                    firstRecommendation = recommendation;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstRecommendation != "") {
                update_form_data(firstRecommendation)
            }

            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Rate a Recommendation
    // ****************************************

    $("#rate-btn").click(function () {

        let reco_id = $("#reco_id").val();
        let rating = $("#reco_rating").val();

        let data = {
            "rating": parseInt(rating),
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/recommendations/${reco_id}/rating`,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

})
