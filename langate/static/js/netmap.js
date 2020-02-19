
window.onload = function () {
    var svg = document.getElementById("map")
    svg.parentElement.replaceChild(svg.contentDocument.documentElement.cloneNode(true), svg);
    var paths = document.querySelectorAll("#insalan_netmap path")

    paths.forEach(function(path) {
        path.addEventListener('click', function(e) {   
                $("#add-team").modal("show")
        })
    })
   
}

/*
$("#create-team-confirm-btn").click(function () {
    console.log("click event")
})
*/