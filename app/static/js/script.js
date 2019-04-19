// custom scripts
$(document).ready(function () {
    $("#last_modified").text(document.lastModified + " - Last Modified"); //don't think this actually does the right thing
    $("#current_time").text(new Date().toLocaleString() + " - Current Time");
});

function redirect(url) {
    window.location.href = url;
}
