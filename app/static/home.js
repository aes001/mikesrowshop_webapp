$(document).ready(function() {

    $(".add-to-basket-button").on("click", function(e) {
        var product = $(this);
        var data = product.attr('data');
        console.log(data);
        e.preventDefault();

        $.ajax({
            url: '/add_to_basket',
            data: data,
            contentType: 'application/json',
            type: 'POST',
            success: function(response) {
                console.log(response);
                product.text("Add more (" + response["quantity"] + " in cart)");
                
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

});