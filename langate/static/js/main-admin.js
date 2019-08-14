/* User delete button onclick handler */

$(document).on("click", ".delete-user-btn", function () {
    let id = $(this).data("userid");
    $("#delete-user-confirm-btn").data("userid", id);

    $.getJSON("/api/user_details/" + id, function (data) {
	$("#delete-user-name").text(data["username"]);
	$("#delete-user-modal").modal("show");
    });
});

/* User modify button onclick handler */

$(document).on("click", ".modify-user-btn", function () {

    let id = $(this).data("userid");
    $("#modify-user-confirm-btn").data("userid", id);

    $("#modify-user-last-name").empty();
    $("#modify-user-first-name").empty();
    $("#modify-user-email").empty();
    $("#modify-user-team").empty();
    $("#modify-user-username").empty();
    $("#modify-user-max-nb-device").empty();

    $.getJSON("/api/user_details/" + id, function (data) {
	$("#modify-user-last-name").val(data["last_name"]);
	$("#modify-user-first-name").val(data["first_name"]);
	$("#modify-user-email").val(data["email"]);
	$("#modify-user-team").val(data["profile"]["team"]);
	$("#modify-user-username").val(data["username"]);
	$("#modify-user-max-nb-device").val(data["profile"]["max_device_nb"]);
	$("#modify-user-tournament option").each(function() { this.selected = (this.text == data["profile"]["tournament"]); });
	$("#modify-user-role option").each(function() { this.selected = (this.text == data["profile"]["role"]); });
    });


    $("#modify-user-modal").modal('show');

});

/* User confirm generate password button onclick handler */

$(document).on("click", "#user-password-warning-confirm-btn", function () {

    let id = $(this).data("userid");

    $.getJSON("/api/user_password/" + id, function (data) {
	$("#user-password-field").text(data["password"]);
	$("#user-password-warning-modal").modal("hide");
	$("#user-password-modal").modal("show");
    });


});

/* User generate password button onclick handler */

$(document).on("click", ".user-password-btn", function () {
    let id = $(this).data("userid");
    $("#user-password-warning-confirm-btn").data("userid", id);

    $.getJSON("/api/user_details/" + id, function (data) {
	$("#user-password-warning-username").text(data["username"]);
	$("#user-password-warning-modal").modal("show");
    });


});


function reload_user_details(id) {

    $("#device-table").empty();
    $("#user-username").empty();
    $("#user-last-name").empty();
    $("#user-first-name").empty();
    $("#user-team").empty();
    $("#user-tournament").empty();
    $("#user-role").empty();

    $.getJSON("/api/user_details/" + id, function (data) {
	$("#user-username").text(data["username"]);
	$("#user-last-name").text(data["last_name"]);
	$("#user-first-name").text(data["first_name"]);
	$("#user-role").text(data["profile"]["role"]);
	$("#user-tournament").text(data["profile"]["tournament"]);
	$("#user-team").text(data["profile"]["team"]);
    });



    $.getJSON("/api/devices_list/"+id, function (data) {

	if (data.length == 0) {
	    $("#device-table").append("<tr><td colspan=\"2\">Aucun périphérique enregistré.</td></tr>")
	}

	else {

	    $.each(data, function (k, dev) {

		$.getJSON("/api/device_status/" + dev["id"], function (data) {

		    let devStatus = "";

		    switch (data["status"]) {

			case "up":
			    devStatus = "<span class=\"badge badge-success\"><i class=\"fas fa-check\"></i></span>";
			    break;

			case "down":
			    devStatus = "<span class=\"badge badge-warning\"><i class=\"fas fa-times\"></i></span>";
			    break;

		    }

		    $("#device-table").append("<tr>\n" +
			"<td>" + dev["name"] + "</td>\n" +
			"<td>" + dev["area"] + "</td>\n" +
			"<td>" + dev["ip"] + "</td>\n" +
			"<td>" + dev["mac"].toUpperCase() + "</td>\n" +
			"<td>" + data["mark"] + "</td>\n" +
			"<td>" + devStatus + "</td>\n" +
			"<td>\n" +
			"<div aria-label=\"Actions\">" +
			//"<button type=\"button\" data-toggle=\"tooltip\" data-placement=\"bottom\" title=\"Consommation données\" class=\"btn btn-sec-insalan device-usage-graph-btn\" data-deviceid=\"" + dev['id'] + "\" aria-label=\"Consommation données\"><span class=\"fas fa-chart-area\" aria-hidden=\"true\"></span></button>\n" +
			"<button type=\"button\" data-toggle=\"tooltip\" data-placement=\"bottom\" title=\"Supprimer l'appareil\" class=\"btn btn-sec-insalan delete-device-btn\" data-deviceid=\"" + dev['id'] + "\" aria-label=\"Supprimer l'appareil\"><span class=\"fas fa-trash\" aria-hidden=\"true\"></span></button>\n" +
			"</div>" +
			"</td>\n" +
			"</tr>\n" +
			"</tr>\n");

		});

	    });

	    $("#device-table").tooltip({offset: "5px, 5px", selector: '[data-toggle=tooltip]'});

	}


    });
	
}


/* User details button onclick handler */

$(document).on("click", ".user-details-btn", function () {
    let id = $(this).data("userid");

    reload_user_details(id);

    $("#user-details-modal").modal("show");

});

/* Device graph button onclick handler */

/*$("#device-table").on("click", ".device-usage-graph-btn", function () {
    let id = $(this).data("deviceid");

    //$("#user-details-modal").modal("hide");

    let chartConf = {

	type: 'line',
	data: {
	    datasets: [{
		label: "Download",
		backgroundColor: 'rgba(0, 0, 0, 0)',
		borderColor: 'rgba(249, 12, 0, 0.8)',
		showLine: true,
		data: [],
	    },

	    {
		label: "Upload",
		backgroundColor: 'rgba(0, 0, 0, 0)',
		borderColor: 'rgba(69, 232, 0, 0.8)',
		showLine: true,
		data: [],
	    }]
	},
	options: {
	    title: {
		display: false,
		text: 'Usage du réseau'
	    },
	    scales: {
		xAxes: [{
		    type: 'time',
		    display: true,
		    scaleLabel: {
			display: true
		    },
		    gridLines: {
			color: 'rgba(255, 255, 255, 0.1)'
		    },
		}],
		yAxes: [{
		    display: true,
		    scaleLabel: {
			type: 'linear',
			display: true,
			labelString: 'Mb/s'
		    },
		    ticks: {
			suggestedMin: 0,
			suggestedMax: 100,
		    },
		    gridLines: {
			color: 'rgba(255, 255, 255, 0.1)'
		    }
		}]
	    },
	    animation: {
		easing: 'linear',
		duration: 1000 * 1.8,
	    }
	}
	// Configuration options go here
    };

    let ctx = $("#device-usage-graph");
    chart = new Chart(ctx, chartConf);

    chartUpdate = setInterval(function () {

	$.getJSON("/api/device_status/" + id, function (data) {
	    d = new Date();
	    chart.data.datasets[0].data.push({x: new Date(d.getTime()), y: data["download"]});
	    chart.data.datasets[1].data.push({x: new Date(d.getTime()), y: data["upload"]});

	    if (chart.data.datasets[0].data.length > 24) {
		chart.data.datasets[0].data.shift();
		chart.data.datasets[1].data.shift();
	    }

	    chart.update();
	});

    }, 2500);

    $("#device-usage-graph-modal").modal("show");


});

// Device graph modal onHide handler

$('#device-usage-graph-modal').on('hidden.bs.modal', function (e) {
    clearInterval(chartUpdate);
});

*/


/* Delete device button onClick handler */

$(document).on("click", ".delete-device-btn", function (e) {
    id = $(this).data("deviceid");
    $("#delete-device-confirm-btn").data("deviceid", id);

    $.getJSON( "/api/device_details/"+id, function( data ) {
       $("#delete-device-name").text(data["name"]);
       $("#delete-device-modal").modal("show");
    });
});



$.ajaxSetup({

    beforeSend: function(xhr, settings) {
	if (!this.crossDomain) {
	    csrftoken = $("[name=csrfmiddlewaretoken]").val();
	    xhr.setRequestHeader("X-CSRFToken", csrftoken);
	}
    }

});

$("#delete-user-confirm-btn").click( function () {

    let id = $(this).data("userid");

    $.ajax({
	url: '/api/user_details/'+id,
	type: 'DELETE',

	success: function(result) {
	    table.ajax.reload();
	},

	error: function (xhr, textStatus, errorThrown) {
	    handle_error(textStatus, errorThrown, xhr.responseText);
	}

    });


    $("#delete-user-modal").modal('hide');


});

$('#create-user-role').on('change', function() {
   if (this.value != "Role.P") {

       if ($("#create-user-max-nb-device-g").hasClass("d-none")){
	   $("#create-user-max-nb-device-g").removeClass("d-none");
       }

   }

   else {

       if (!$("#create-user-max-nb-device-g").hasClass("d-none")){
	   $("#create-user-max-nb-device-g").addClass("d-none");
       }

   }
});

$('#create-user-modal').on('show.bs.modal', function (e) {
    $("#create-user-feedback").empty();
    $("#create-user-feedback").addClass("d-none");
});

$("#create-user-btn").click( function () {

    let data = {
	"first_name": $("#create-user-first-name").val(),
	"last_name": $("#create-user-last-name").val(),
	"username": $("#create-user-username").val(),
	"email": $("#create-user-email").val(),
	"is_active": true,
	"profile": {
	    "max_device_nb": $("#create-user-max-nb-device").val(),
	    "role": $("#create-user-role").val(),
	    "tournament": ($("#create-user-tournament").val() != "no") ? $("#create-user-tournament").val() : null,
	    "team": ($("#create-user-team").val() != "") ? $("#create-user-team").val() : null
	}
    };

    $.ajax({
	url: '/api/user_list/',
	type: 'POST',
	contentType: "application/json; charset=utf-8",
	data : JSON.stringify(data),

	success: function(result) {

	    if ($("#create-user-password").val() == "") {
		$.getJSON("/api/user_password/" + result["id"], function (data) {
		    $("#create-user-feedback").removeClass("d-none");
		    $("#create-user-feedback").append("<div class=\"alert alert-success-insalan\" role=\"alert\"><strong>Utilisateur " + result["username"] + " créé avec succès !</strong><br>Mot de passe de connexion : <strong>" + data["password"] + "</strong>.</div>")
		});
	    }

	    else {
		$.ajax({
		    url: '/api/user_password/'+result["id"],
		    type: 'POST',
		    contentType: "application/json; charset=utf-8",
		    data : JSON.stringify({ "password" : $("#create-user-password").val() }),

		    success: function(data) {
			$("#create-user-feedback").append("<div class=\"alert alert-success-insalan\" role=\"alert\"><strong>Utilisateur " + result["username"] + " créé avec succès !</strong></div>")
		    },

		    error: function (xhr, textStatus, errorThrown) {
			handle_error(textStatus, errorThrown, xhr.responseText);
		    }

		});

	    }

	    $("#create-user-form")[0].reset();
	    $("#create-user-feedback").empty();

	    $("#create-user-last-name").focus();
		    table.ajax.reload();
	},


	error: function (xhr, textStatus, errorThrown) {
	    handle_error(textStatus, errorThrown, xhr.responseText);
	}

    });


});

$("#modify-user-confirm-btn").click( function () {

    let id = $(this).data("userid");

    let data = {
	"first_name": $("#modify-user-first-name").val(),
	"last_name": $("#modify-user-last-name").val(),
	"username": $("#modify-user-username").val(),
	"email": $("#modify-user-email").val(),
	"is_active": true,
	"profile": {
	    "max_device_nb": $("#modify-user-max-nb-device").val(),
	    "role": $("#modify-user-role").val(),
	    "tournament": ($("#modify-user-tournament").val() != "no") ? $("#modify-user-tournament").val() : null,
	    "team": ($("#modify-user-team").val() != "") ? $("#modify-user-team").val() : null
	}
    };

    $.ajax({
	url: '/api/user_details/'+id,
	type: 'PUT',
	contentType: "application/json; charset=utf-8",
	data : JSON.stringify(data),

	success: function(result) {
	    $("#modify-user-modal").modal('hide');
	    table.ajax.reload();
	},

	error: function (xhr, textStatus, errorThrown) {
	    handle_error(textStatus, errorThrown, xhr.responseText);
	}

    });
    

});



$("#delete-device-confirm-btn").click(function () {

    let id = $(this).data("deviceid");

    $.ajax({
	url: '/api/device_details/' + id + '/',
	type: 'DELETE',

	success: function (result) {
		reload_user_details(id);
	},

	error: function (xhr, textStatus, errorThrown) {
	    handle_error(textStatus, errorThrown, xhr.responseText);
	}

    });

    $("#delete-device-modal").modal('hide');

});

function reload_pizzas_settings() {
                                                                                                                                                                                                                                                                                                                                                       
    $.getJSON( "/api/widgets/pizzas/", function( data ) {
        $("#pizzas-visible").prop('checked', data["visible"]);
        $("#pizzas-online-order-url").val(data["online_order_url"]);
    });
                                                                                                                                                                                                                                                                                                                                                       
}
                                                                                                                                                                                                                                                                                                                                                       
function reload_pizza_slots_table() {
                                                                                                                                                                                                                                                                                                                                                       
    $("#pizza-slots-table").empty();
                                                                                                                                                                                                                                                                                                                                                       
    $.getJSON( "/api/widgets/pizzas/slots/", function( data ) {
                                                                                                                                                                                                                                                                                                                                                       
        if (data.length == 0) {
            $("#pizza-slots-table").append("<tr><td colspan=\"5\" class=\"text-center\">Aucun créneau n'est enregistré.</td></tr>")
        }
                                                                                                                                                                                                                                                                                                                                                       
        else {
                                                                                                                                                                                                                                                                                                                                                       
            let i = 1;
                                                                                                                                                                                                                                                                                                                                                       
            $.each(data, function (k, a) {
                                                                                                                                                                                                                                                                                                                                                       
                $("#pizza-slots-table").append("<tr>\n" +
                    "                    <th scope=\"row\">" + i + "</th>\n" +
                    "                    <td>" + a.orders_begin + "</td>\n" +
                    "                    <td>" + a.orders_end + "</td>\n" +
                    "                    <td>" + a.delivery + "</td>\n" +
                    "                    <td>\n" +
                    "                        <div class=\"text-center\" role=\"group\" aria-label=\"Actions\">\n" +
                    "                            <button type=\"button\" data-toggle=\"tooltip\" data-placement=\"bottom\" title=\"Supprimer le créneau\" class=\"btn btn-sec-insalan delete-pizza-slot-btn\" data-slotid=\"" + a.id + "\" aria-label=\"Supprimer le créneau\"><span class=\"fas fa-trash\" aria-hidden=\"true\"></span></button>\n" +
                    "                        </div>\n" +
                    "                    </td>\n" +
                    "                </tr>");
                                                                                                                                                                                                                                                                                                                                                       
                i++;
                                                                                                                                                                                                                                                                                                                                                       
            });
                                                                                                                                                                                                                                                                                                                                                       
        }
    });
}
                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                       
function reload_announces_table() {
                                                                                                                                                                                                                                                                                                                                                       
    $("#announces-table").empty();
                                                                                                                                                                                                                                                                                                                                                       
    $.getJSON( "/api/widgets/announce/", function( data ) {
                                                                                                                                                                                                                                                                                                                                                       
        if (data.length == 0) {
            $("#announces-table").append("<tr><td colspan=\"5\" class=\"text-center\">Aucune annonce n'est enregistrée.</td></tr>")
        }
                                                                                                                                                                                                                                                                                                                                                       
        else {
                                                                                                                                                                                                                                                                                                                                                       
            let i = 1;
                                                                                                                                                                                                                                                                                                                                                       
            $.each(data, function (k, a) {
                                                                                                                                                                                                                                                                                                                                                       
                let content = a.content.substring(0, 50) + " ...";
                                                                                                                                                                                                                                                                                                                                                       
                $("#announces-table").append("<tr>\n" +
                    "                    <th scope=\"row\">" + i + "</th>\n" +
                    "                    <td>" + a.title + "</td>\n" +
                    "                    <td>" + content + "</td>\n" +
                    "                    <td>" + ( (a.visible) ? "<span class=\"badge badge-success\"><i class=\"fas fa-check\"></i></span>" : "<span class=\"badge badge-danger\"><i class=\"fas fa-times\"></i></span>" ) + "</td>\n" +
                    "                    <td>\n" +
                    "                        <div class=\"text-center\" role=\"group\" aria-label=\"Actions\">\n" +
                    "                            <button type=\"button\" data-toggle=\"tooltip\" data-placement=\"bottom\" title=\"Modifier l'annonce\" class=\"btn btn-sec-insalan modify-announce-btn\" data-announceid=\"" + a.id + "\" aria-label=\"Modifier l'annonce\"><span class=\"fas fa-pen\" aria-hidden=\"true\"></span></button>\n" +
                    "                            <button type=\"button\" data-toggle=\"tooltip\" data-placement=\"bottom\" title=\"Supprimer l'annonce\" class=\"btn btn-sec-insalan delete-announce-btn\" data-announceid=\"" + a.id + "\" aria-label=\"Supprimer l'annonce\"><span class=\"fas fa-trash\" aria-hidden=\"true\"></span></button>\n" +
                    "                        </div>\n" +
                    "                    </td>\n" +
                    "                </tr>");
                                                                                                                                                                                                                                                                                                                                                       
                i++;
                                                                                                                                                                                                                                                                                                                                                       
            });
                                                                                                                                                                                                                                                                                                                                                       
        }
                                                                                                                                                                                                                                                                                                                                                       
    });
}
                                                                                                                                                                                                                                                                                                                                                       
function reload_realtime_status_settings() {
                                                                                                                                                                                                                                                                                                                                                       
    $.getJSON( "/api/widgets/status", function( data ) {
        $("#realtime-visible").prop('checked', data["visible"]);
        $("#realtime-lan-status").val("Status."+data["lan"]);
        $("#realtime-wan-status").val("Status."+data["wan"]);
        $("#realtime-csgo-status").val("Status."+data["csgo"]);
    });
                                                                                                                                                                                                                                                                                                                                                       
}
                                                                                                                                                                                                                                                                                                                                                       
$('a[data-toggle="tab"]').on('show.bs.tab', function (e) {
    let id = e.target.id;
                                                                                                                                                                                                                                                                                                                                                       
    if (id == "widget-announces-tab") {
        reload_announces_table();
    }
                                                                                                                                                                                                                                                                                                                                                       
    if (id == "widget-realtime-status-tab") {
        reload_realtime_status_settings();
    }
                                                                                                                                                                                                                                                                                                                                                       
    if (id == "widget-pizzas-tab") {
        reload_pizzas_settings();
        reload_pizza_slots_table();
    }
});
                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                       
$(document).on("click", ".delete-announce-btn", function (e) {
    let id = $(this).data("announceid");
    $("#delete-announce-confirm-btn").data("announceid", id);
    $("#delete-announce-modal").modal("show");
});
                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                       
$("#delete-announce-confirm-btn").click( function () {
                                                                                                                                                                                                                                                                                                                                                       
    let id = $(this).data("announceid");
                                                                                                                                                                                                                                                                                                                                                       
    $.ajax({
        url: '/api/widgets/announce/'+id,
        type: 'DELETE',
                                                                                                                                                                                                                                                                                                                                                       
        success: function(result) {
            reload_announces_table();
        },
                                                                                                                                                                                                                                                                                                                                                       
        error: function (xhr, textStatus, errorThrown) {
            handle_error(textStatus, errorThrown, xhr.responseText);
        }
    });
                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                       
    $("#delete-announce-modal").modal("hide");
                                                                                                                                                                                                                                                                                                                                                       
});

$("#create-announce-btn").click( function () {
                                                                                                                                                                                                                                                                                                                                                       
    let data = {
        "visible": $("#create-announce-visible").is(':checked'),
        "title": $("#create-announce-title").val(),
        "content": $("#create-announce-content").val()
    };
                                                                                                                                                                                                                                                                                                                                                       
    if (!/^[^<>]+$/.test(data["title"])  || data["title"].length > 50) {
        create_error_modal("Oops", "<p>Le titre de l'annonce ne peut pas faire plus de 50 caractères ou contenir les caractères <b>&lt;</b> et <b>&gt;</b>.</p>");
    }
                                                                                                                                                                                                                                                                                                                                                       
    else if (!/^[^<>]+$/.test(data["content"])) {
        create_error_modal("Oops", "<p>Le contenu l'annonce ne peut pas contenir les caractères <b>&lt;</b> et <b>&gt;</b>.</p>");
    }
                                                                                                                                                                                                                                                                                                                                                       
    else {
                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                       
        $.ajax({
            url: '/api/widgets/announce/',
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(data),
                                                                                                                                                                                                                                                                                                                                                       
            success: function (result) {
                reload_announces_table();
            },
                                                                                                                                                                                                                                                                                                                                                       
            error: function (xhr, textStatus, errorThrown) {
                handle_error(textStatus, errorThrown, xhr.responseText);
            }
                                                                                                                                                                                                                                                                                                                                                       
        });
                                                                                                                                                                                                                                                                                                                                                       
    }
                                                                                                                                                                                                                                                                                                                                                       
    $("#create-announce-modal").modal("hide");
                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                       
});
                                                                                                                                                                                                                                                                                                                                                       
$(document).on("click", ".modify-announce-btn", function () {
                                                                                                                                                                                                                                                                                                                                                       
    let id = $(this).data("announceid");
    $("#modify-announce-confirm-btn").data("announceid", id);
                                                                                                                                                                                                                                                                                                                                                       
    $("#modify-announce-visible").prop('checked', false);
    $("#modify-announce-title").empty();
    $("#modify-announce-content").empty();
                                                                                                                                                                                                                                                                                                                                                       
    $.getJSON("/api/widgets/announce/" + id, function (data) {
        $("#modify-announce-visible").prop('checked', data["visible"]);
        $("#modify-announce-title").val(data["title"]);
        $("#modify-announce-content").val(data["content"]);
    });
                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                       
    $("#modify-announce-modal").modal('show');
                                                                                                                                                                                                                                                                                                                                                       
});
                                                                                                                                                                                                                                                                                                                                                       
$("#modify-announce-confirm-btn").click( function () {
                                                                                                                                                                                                                                                                                                                                                       
    let id = $(this).data("announceid");
    let data = {
        "visible": $("#modify-announce-visible").is(':checked'),
        "title": $("#modify-announce-title").val(),
        "content": $("#modify-announce-content").val()
    };
                                                                                                                                                                                                                                                                                                                                                       
    if (!/^[^<>]+$/.test(data["title"])  || data["title"].length > 50) {
        create_error_modal("Oops", "<p>Le titre de l'annonce ne peut pas faire plus de 50 caractères ou contenir les caractères <b>&lt;</b> et <b>&gt;</b>.</p>");
    }
                                                                                                                                                                                                                                                                                                                                                       
    else if (!/^[^<>]+$/.test(data["content"])) {
        create_error_modal("Oops", "<p>Le contenu l'annonce ne peut pas contenir les caractères <b>&lt;</b> et <b>&gt;</b>.</p>");
    }
                                                                                                                                                                                                                                                                                                                                                       
    else {
                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                       
        $.ajax({
            url: '/api/widgets/announce/' + id,
            type: 'PUT',
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(data),
                                                                                                                                                                                                                                                                                                                                                       
            success: function (result) {
                reload_announces_table();
            },
                                                                                                                                                                                                                                                                                                                                                       
            error: function (xhr, textStatus, errorThrown) {
                handle_error(textStatus, errorThrown, xhr.responseText);
            }
                                                                                                                                                                                                                                                                                                                                                       
        });
                                                                                                                                                                                                                                                                                                                                                       
    }
                                                                                                                                                                                                                                                                                                                                                       
    $("#modify-announce-modal").modal("hide");
                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                       
});
                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                       
$("#realtime-confirm-btn").click(function () {
    $("#realtime-feedback").empty();
                                                                                                                                                                                                                                                                                                                                                       
    let data  = {
        "visible": $("#realtime-visible").prop('checked'),
        "lan": $("#realtime-lan-status").val(),
        "wan": $("#realtime-wan-status").val(),
        "csgo": $("#realtime-csgo-status").val()
    };
                                                                                                                                                                                                                                                                                                                                                       
    $.ajax({
        url: '/api/widgets/status/',
        type: 'POST',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(data),
                                                                                                                                                                                                                                                                                                                                                       
        success: function (result) {
            reload_realtime_status_settings();
                                                                                                                                                                                                                                                                                                                                                       
            $("#realtime-feedback").append("<div class=\"alert alert-success-insalan\" role=\"alert\"><strong>Mise à jour effectuée.</strong></div>");
            setTimeout(function () { $("#realtime-feedback").empty() }, 6000);
        },
                                                                                                                                                                                                                                                                                                                                                       
        error: function (xhr, textStatus, errorThrown) {
            handle_error(textStatus, errorThrown, xhr.responseText);
        }
                                                                                                                                                                                                                                                                                                                                                       
    });
                                                                                                                                                                                                                                                                                                                                                       
});
                                                                                                                                                                                                                                                                                                                                                       
$(document).on("click", ".delete-pizza-slot-btn", function (e) {
    let id = $(this).data("slotid");
    $("#delete-pizza-slot-confirm-btn").data("slotid", id);
    $("#delete-pizza-slot-modal").modal("show");
});
                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                       
$("#delete-pizza-slot-confirm-btn").click( function () {
                                                                                                                                                                                                                                                                                                                                                       
    let id = $(this).data("slotid");
                                                                                                                                                                                                                                                                                                                                                       
    $.ajax({
        url: '/api/widgets/pizzas/slots/'+id,
        type: 'DELETE',
                                                                                                                                                                                                                                                                                                                                                       
        success: function(result) {
            reload_pizza_slots_table();
        },
                                                                                                                                                                                                                                                                                                                                                       
        error: function (xhr, textStatus, errorThrown) {
            handle_error(textStatus, errorThrown, xhr.responseText);
        }
    });
                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                       
    $("#delete-pizza-slot-modal").modal("hide");
                                                                                                                                                                                                                                                                                                                                                       
});
                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                       
$("#create-pizza-slot-btn").click( function () {
                                                                                                                                                                                                                                                                                                                                                       
    let data = {
        "orders_begin": $("#create-pizza-slot-orders-begin").val(),
        "orders_end": $("#create-pizza-slot-orders-end").val(),
        "delivery": $("#create-pizza-slot-delivery").val()
    };
                                                                                                                                                                                                                                                                                                                                                       
    $.ajax({
        url: '/api/widgets/pizzas/slots/',
        type: 'POST',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(data),
                                                                                                                                                                                                                                                                                                                                                       
        success: function (result) {
            reload_pizzas_settings();
            reload_pizza_slots_table();
        },
                                                                                                                                                                                                                                                                                                                                                       
        error: function (xhr, textStatus, errorThrown) {
            handle_error(textStatus, errorThrown, xhr.responseText);
        }
                                                                                                                                                                                                                                                                                                                                                       
    });
                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                       
    $("#create-pizza-slot-modal").modal("hide");
                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                       
});
                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                       
$("#pizzas-confirm-btn").click(function () {
    $("#pizzas-feedback").empty();
                                                                                                                                                                                                                                                                                                                                                       
    let data  = {
        "visible": $("#pizzas-visible").prop('checked')
    };
                                                                                                                                                                                                                                                                                                                                                       
    $.ajax({
        url: '/api/widgets/pizzas/',
        type: 'POST',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(data),
                                                                                                                                                                                                                                                                                                                                                       
        success: function (result) {
            reload_pizza_slots_table();
                                                                                                                                                                                                                                                                                                                                                       
            $("#pizzas-feedback").append("<div class=\"alert alert-success-insalan\" role=\"alert\"><strong>Mise à jour effectuée.</strong></div>");
            setTimeout(function () { $("#pizzas-feedback").empty() }, 6000);
        },
                                                                                                                                                                                                                                                                                                                                                       
        error: function (xhr, textStatus, errorThrown) {
            handle_error(textStatus, errorThrown, xhr.responseText);
        }
                                                                                                                                                                                                                                                                                                                                                       
    });
                                                                                                                                                                                                                                                                                                                                                       
});
