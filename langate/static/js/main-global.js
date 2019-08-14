// Workaround to include the CSRF token into all AJAX requests because the API needs it.
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
	if (!this.crossDomain) {
	    csrftoken = $("[name=csrfmiddlewaretoken]").val();
	    xhr.setRequestHeader("X-CSRFToken", csrftoken);
	}
    }

});
