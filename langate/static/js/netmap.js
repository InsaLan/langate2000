

window.onload = function () {
    var rects = document.querySelectorAll("#insalan_netmap rect")

    rects.forEach(function(rect) {
        rect.addEventListener('click', function(e) {   
            $("#delete-user-modal").modal("show");
        })
    })

    users_list = []
    $.getJSON("/api/user_list")
    .done(function(users) {
        users.forEach(function(user) {
            $.getJSON("/api/devices_list_by_name/"+user.username)
            .done(function(devices) {
                ip_list = []
                devices.forEach(device => {
                    ip_list.push(device.ip)
                })
                users_list[user.username] = ip_list
            })
        })
    })
    .fail(function(error) {
        alert(error)
    })
    
    console.log(users_list)
    $.getJSON("/api/bandwidth_by_ip/<str:ip>")
    .done()
    $.getJSON("/api/teams")
    .done(function(teams) {
        teams.forEach(function(team) {
            if(team.placement) {
                map_id = team.tournament + "-" + team.placement
                document.getElementById(map_id).innerHTML = "<title>"+team.name+"</title>"
                document.getElementById(map_id).classList.add('taken_seats');
                console.log(team.user_names)
            }
          
        })
    })
    .fail(function(error) {
        console.error(error)
    })
    
   
}

