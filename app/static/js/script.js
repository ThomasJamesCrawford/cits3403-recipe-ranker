// custom scripts

// jquery document ready
$(document).ready(function () {
    // set current time 
    $("#current_time").text(new Date().toLocaleString() + " - Current Time");

    // clickable table row with specified href
    $(".clickable-table-row").click(function () {
        window.location = $(this).data("href");
    });

    // uses the html5 validity popup is password dont match
    $("#password_repeat").on("input", function() {
        if($("#password_repeat").val() != $("#password").val())
        {
            $("#password_repeat")[0].setCustomValidity("Passwords Must Match");
        } else {
            $("#password_repeat")[0].setCustomValidity("");
        }
    });
});

function redirect(url) {
    window.location.href = url;
}

// add a recipe form from template below to the recipes div
function addRecipe() {
    $count = $('#recipes').children().length;
    $form = $(
        '<p>' +
        '<label class="form-control-label" for="recipes-' + $count + '-name">Recipe Name</label> <br>' +
        '<input class="form-control form-control-lg" id="recipes-0-name" name="recipes-' + $count + '-name" required size="64" type="text" value=""> <br>' +
        '<label class="form-control-label" for="recipes-' + $count + '-description">Recipe Description</label> <br>' +
        '<textarea class="form-control form-control-lg" id="recipes-' + $count + '-description" name="recipes-' + $count + '-description" required size="128" type="text" value="">' +
        '</p>'
    );

    $('#recipes').append($form);
}

// build delete_vote(vote_id) url and open modal
// url_for(delete_vote, vote_id=vote_id)
function deleteVote(vote_id) {
    $("#deleteVoteForm").attr('action', '/vote/' + vote_id + '/delete');
    $("#deleteVoteModal").modal();
}

// submit a vote for the checked recipe as current user
function submitVote(poll_id) {
    // get checked value
    $recipe_id = $("input[name=recipe-vote" + poll_id + "]:checked").val();

    // build the url
    $("#voteForm" + poll_id).attr('action', '/recipe/' + $recipe_id + '/vote');

    // submit the form
    if($recipe_id != null){
        $("#voteForm" + poll_id).submit();
    } else {
        // havent selected a vote do nothing
    }
}
