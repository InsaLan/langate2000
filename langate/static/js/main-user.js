function reload_device_table() {
    $("#device-table").empty();
    $.getJSON( "/api/devices_list/"+user_id, function( data ) {
        let i = 1;
                                                                                                                                                                                                                                                                                                                                                                                  
        $.each(data, function (k, dev) {
                                                                                                                                                                                                                                                                                                                                                                                  
            let dev_hint = (dev.ip == current_ip) ? " <b>(cet appareil)</b>" : "";
            let current_dev = (dev.ip == current_ip) ? "yes" : "no";
                                                                                                                                                                                                                                                                                                                                                                                  
            $("#device-table").append("<tr>\n" +
                "                    <th scope=\"row\">"+i+"</th>\n" +
                "                    <td>"+dev.name+dev_hint+"</td>\n" +
                "                    <td>"+dev.area+"</td>\n" +
                "                    <td>\n" +
                "                        <div class=\"text-center\" role=\"group\" aria-label=\"Actions\">\n" +
                "                            <button type=\"button\" data-toggle=\"tooltip\" data-placement=\"bottom\" title=\"Modifier l'appareil\" class=\"btn btn-sec-insalan modify-device-btn\" data-deviceid=\""+dev.id+"\" data-iscurrent=\""+current_dev+"\"><span class=\"fas fa-pen\" aria-hidden=\"true\"></span></button>\n" +
                "                            <button type=\"button\" data-toggle=\"tooltip\" data-placement=\"bottom\" title=\"Supprimer l'appareil\" class=\"btn btn-sec-insalan delete-device-btn\" data-deviceid=\""+dev.id+"\" data-iscurrent=\""+current_dev+"\" aria-label=\"Supprimer l'appareil\"><span class=\"fas fa-trash\" aria-hidden=\"true\"></span></button>\n" +
                "                        </div>\n" +
                "                    </td>\n" +
                "                </tr>");
                                                                                                                                                                                                                                                                                                                                                                                  
            i++;
                                                                                                                                                                                                                                                                                                                                                                                  
        });
    });
}

/*
 * UI event listeners
 */

$(document).on("click", ".delete-device-btn", function (e) {
    let id = $(this).data("deviceid");
    let iscurrent = $(this).data("iscurrent");

    $("#delete-device-confirm-btn").data("deviceid", id);
    $("#delete-device-confirm-btn").data("iscurrent", iscurrent);

    $.getJSON( "/api/device_details/"+id, function( data ) {
       $("#delete-device-name").text(data["name"]);
       $("#delete-device-modal").modal("show");
    });
});

$(document).on("click", ".modify-device-btn", function (e) {
    let id = $(this).data("deviceid");
    $("#modify-device-confirm-btn").data("deviceid", id);

    $.getJSON( "/api/device_details/"+id, function( data ) {
	$("#modify-device-name").val(data["name"]);
    });

    $("#modify-device-modal").modal("show");
});

$("#delete-device-confirm-btn").click( function () {

    let id = $(this).data("deviceid");
    let iscurrent = $(this).data("iscurrent") == "yes";

    $.ajax({
	url: '/api/device_details/' + id + '/',
	type: 'DELETE',

	success: function (result) {

	    if (too_many_devices || iscurrent) {
		location.reload();
	    }

	    else {
		reload_device_table();
	    }
	},

	error: function (xhr, textStatus, errorThrown) {
	    handle_error(textStatus, errorThrown, xhr.responseText);
	}

    });

    $("#delete-device-modal").modal('hide');


});

$("#modify-device-confirm-btn").click( function () {

    let name = $("#modify-device-name").val();

    if (!/^[^<>]+$/.test(name) || name.length > 100) {
	create_error_modal("Oops", "<p>Le nom d'un appareil doit faire de 1 à 100 caractères et peut contenir n'importe quel caractère à l'exception des caractères <b>&lt;</b> et <b>&gt;</b>.</p>");
    }

    else {

	let id = $(this).data("deviceid");

	$.ajax({
	    url: '/api/device_details/' + id + '/',
	    type: 'PUT',
	    data: "name=" + encodeURI(name),

	    success: function (result) {
		reload_device_table();
	    },

	    error: function (xhr, textStatus, errorThrown) {
		handle_error(textStatus, errorThrown, xhr.responseText);
	    }
	});


    }

    $("#modify-device-modal").modal('hide');

});

$(".faq-question").click(function () {
    if ($(this).attr('aria-expanded') === "false") {
	$(this).children().removeClass("fa-caret-down");
	$(this).children().addClass("fa-caret-up");
    }
    else {
	$(this).children().removeClass("fa-caret-up");
	$(this).children().addClass("fa-caret-down");
    }
});

// Client-side workaround to prevent multiple form submission
// if the user presses multiple times the enter key.
$(document).on("submit", ".form-auth", function () {
  $(this).find(':submit').attr('disabled','disabled');
});
