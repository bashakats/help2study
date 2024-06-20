$.getScript("https://js.braintreegateway.com/web/dropin/1.40.2/js/dropin.min.js", function () {

    let button = document.querySelector('#donateButton');
    let messageElement = document.getElementById("response-message")
    let dropInContainer = document.getElementById("bt-drop-in")

    braintree.dropin.create(
        {
            authorization: braintree_client_token,
            container: dropInContainer,
            card: {
                cardholderName: {
                    required: false
                }
            },
            paypal: {
                //                flow: 'vault',
                flow: 'checkout',
                amount: '10.00',
                currency: 'USD'
            }
        },
        function (createErr, instance) {

            if (createErr) {
                messageElement.innerHtml = '<h1>Error</h1><p>Something went wrong. Could not complete the donation. <br> </p>';
                CustomFormSubmitResponse($('#donateButton'));
            }
            button.addEventListener('click', function (event) {
                event.preventDefault();
                instance.requestPaymentMethod(function (err, payload) {
                    if (err) {
                        messageElement.innerHtml = '<h1>Error</h1><p>Something went wrong. Could not complete the donation. <br> </p>';
                        CustomFormSubmitResponse($('#donateButton'));
                    }
                    CustomFormSubmitPost($('#donateButton'));
                    $.ajaxSetup({
                        headers: {
                            'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
                        }
                    });

                    $.ajax({
                        type: 'POST',
                        url: paymentUrl,
                        data: {
                            paymentNonce: payload.nonce,
                            amount: price,
                            currency: "USD",
                            description: sub_name,
                        },
                        success: function (json) {
                            if (json['result'] == 'okay') {
                                showDialog()
                            } else {
                                messageElement.innerHtml = '<h1>Error</h1><p>Something went wrong. Could not complete the donation.</p>';
                                CustomFormSubmitResponse($('#donateButton'));
                                alert(json["message"]);

                            }
                        },
                        error: function (xhr) {
                            CustomFormSubmitResponse($('#donateButton'));
                            console.log(xhr.status + ": " + xhr.responseText);
                        }
                    }).done(function (result) {
                        CustomFormSubmitResponse($('#donateButton'));
                    });
                });
            });

        }
    );
})


$("#saved-cards tr").click(function () {
    $(this).addClass('selected').siblings().removeClass('selected');
    let value = $(this).find('td:first').html();
    $('#use-card').removeAttr("disabled")
});

$('.ok').on('click', function (e) {
    alert($("#saved-cards tr.selected td:first").html());
});



let messageElement = document.getElementById("response-message")
let redirectElement = document.getElementById("redirect-timer")
function payWithSavedCard() {
    CustomFormSubmitPost($('#use-card'));
    $.ajax({
        method: "POST",
        url: paymentUrl,
        data: {
            amount: price,
            currency: "USD",
            description: sub_name,
            card_id: $("#saved-cards tr.selected td:first").html(),
        },
        success: function (json) {

            if (json["result"] == "okay") {
                alert("Your payment was a success");
                messageElement.innerHtml = '<h1>The Donation was received and is much appreciated</h1><p>we thank you dearly for the kind heart.</p>';
                for (let i = 4; i > 0; i--) {
                    setTimeout(function () {
                        messageElement.innerHtml = `<p>Returning you to the home page in${i}!.</p>`;
                    }, 1000);
                }

                setTimeout(function () {
                    window.location.assign(redirectUrl)
                }, 5000);
            } else {
                CustomFormSubmitResponse($('#use-card'));
                alert(json["message"]);
            }
        },
        error: function (xhr) {
            CustomFormSubmitResponse($('#use-card'));
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });

}


let temp_button_text;

function CustomFormSubmitResponse(e) {
    $(e).removeAttr('disabled').text(temp_button_text);
};

function CustomFormSubmitPost(e) {
    let el = $(e);
    temp_button_text = el.text()
    el.attr('disabled', 'disabled').text("").append('<role="status" aria-hidden="true"></span>Loading...');
};


$(function () {
    // This function gets cookie with a given name
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie != '') {
            let cookies = document.cookie.split(';');
            for (const element of cookies) {
                let cookie = jQuery.trim(element);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    let csrftoken = getCookie('csrftoken');
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        let host = document.location.host; // host + port
        let protocol = document.location.protocol;
        let sr_origin = '//' + host;
        let origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
})