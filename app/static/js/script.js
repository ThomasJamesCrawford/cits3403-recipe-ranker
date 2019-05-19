// custom scripts

// jquery document ready
$(document).ready(function () {
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

function addRecipe() {
    $count = $('#recipes').children().length;
    //$csrf_token = $('#csrf_token').attr('value');
    $form = $(
        '<p>' +
        '<label for="recipes-' + $count + '-name">Recipe Name</label> <br>' +
        '<input id="recipes-0-name" name="recipes-' + $count + '-name" required size="64" type="text" value=""> <br>' +
        '<label for="recipes-' + $count + '-description">Recipe Description</label> <br>' +
        '<input id="recipes-' + $count + '-description" name="recipes-' + $count + '-description" required size="128" type="text" value=""> <br>' +
        //'<input type="hidden" id="csrf_token" name="csrf_token" value="' + $csrf_token + '" />' +
        '</p'
    );

    $('#recipes').append($form);
}

function deleteVote(vote_id) {
    $("#deleteVoteForm").attr('action', '/vote/' + vote_id + '/delete');
    $("#deleteVoteModal").modal();
}

function submitVote(poll_id) {
    $recipe_id = $("input[name=recipe-vote" + poll_id + "]:checked").val();

    $("#voteForm" + poll_id).attr('action', '/recipe/' + $recipe_id + '/vote');

    if($recipe_id != null){
        $("#voteForm" + poll_id).submit();
    } else {
        // havent selected a vote do nothing
    }
}
