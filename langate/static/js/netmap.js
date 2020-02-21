

window.onload = function () {
    var rects = document.querySelectorAll("#insalan_netmap rect")

    rects.forEach(function(rect) {
        rect.addEventListener('click', function(e) {   
            $("#delete-user-modal").modal("show");
        })
    })

    users_tuple = []
    $.getJSON("/api/user_list")
    .done(function(users) {
        users.forEach(function(user) {
            $.getJSON("/api/devices_list_by_name/"+user.username)
            .done(function(devices) {
                users_tuple.push({
                    key: user.username,
                    value: devices})

                console.log(users_tuple)
            })
        })
    })
    .fail(function(error) {
        alert(error)
    })

    $.getJSON("/api/teams")
    .done(function(teams) {
        teams.forEach(function(team) {
            if(team.placement) {
                map_id = team.tournament + "-" + team.placement
                document.getElementById(map_id).innerHTML = "<title>"+team.name+"</title>"
                document.getElementById(map_id).classList.add('taken_seats');
                
            }
          
        })
    })
    .fail(function(error) {
        alert(error)
    })
    
   
}

