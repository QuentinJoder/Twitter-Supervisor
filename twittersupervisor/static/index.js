const api_prefix = "/api"

$(document).ready(function() {

     // Activate the correct nav-link
    $(".nav-link").each( function (index) {
        if(window.location.pathname.startsWith($(this).attr("href"))) {
            $(this).addClass("active");
        }
    });

    // Accordion collapse in 'Followers' and 'Unfollowers'
    $(".accordion-button").click(function (){
        var targetId = $(this).attr("data-bs-target");
        var followerId = targetId.substring(targetId.indexOf("-") + 1);

        if( $(this).hasClass("collapsed")) {
            $(targetId).addClass("show");
            $(this).removeClass("collapsed");

            $.getJSON(api_prefix+"/followers/" + followerId + "/events", function(response) {
                $.each(response, function(key, value) {
                    tr = $('<tr>');
                    tr.append($('<td>').text(value.event_date)); // TODO: Decide what date format to use
                    tr.append($('<td>').text(value.following ? "Follow" : "Unfollow"));
                    $("#tbody-" + followerId).append(tr);
                });
            });
        } else {
            $($(this).attr("data-bs-target")).removeClass("show");
            $(this).addClass("collapsed");
            $("#tbody-" + followerId).empty();
        }

    });

});