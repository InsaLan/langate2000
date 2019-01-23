function create_error_modal(title, content) {
    if ($("#error-modal")) { $("#error-modal").remove(); } // If an error modal already exists, we remove it so that we can show the new one.

    $(document.body).append("<div class=\"modal modal-insalan\" id=\"error-modal\" tabindex=\"-1\" role=\"dialog\" aria-hidden=\"true\">\n" +
                            "        <div class=\"modal-dialog modal-dialog-centered\" role=\"document\">\n" +
                            "            <div class=\"modal-content\">\n" +
                            "                <div class=\"modal-header\">\n" +
                            "                    <h5 class=\"modal-title\">"+title+"</h5>\n" +
                            "                    <button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-label=\"Close\">\n" +
                            "                        <span aria-hidden=\"true\">&times;</span>\n" +
                            "                    </button>\n" +
                            "                </div>\n" +
                            "                <div class=\"modal-body text-white\">\n" + content +
                            "                </div>\n" +
                            "                <div class=\"modal-footer\">\n" +
                            "                    <button type=\"button\" class=\"btn btn-secondary\" data-dismiss=\"modal\">Fermer</button>\n" +
                            "                </div>\n" +
                            "            </div>\n" +
                            "        </div>\n" +
                            "    </div>\n");

    $('#error-modal').modal('show');
}

function handle_error(errorType, errorTitle, errorString) {
    switch (errorType) {
        case "error":

            try {
                let errors = JSON.parse(errorString);

                if (errors.hasOwnProperty("detail")) {
                    create_error_modal("Erreur de l'API", "<p>Le serveur a renvoyé l'erreur suivante lors du traitement de la requete : </p><code>"+errors.detail+"</code>");
                }

                else {
                    let s = "";

                    for (let field in errors) {
                        s += "<p>Champ <b>"+field+"</b></p>";
                        s += "<ul>";

                        for (let err in errors[field]) {
                            s+= "<li>"+errors[field][err]+"</li>";
                        }
                        s += "</ul>";
                    }

                    create_error_modal("Erreur de validation","<p>Le serveur a renvoyé les erreurs suivantes durant la validation de la requete : </p>"+s);
                }



            }
            catch (e) {
                create_error_modal("Erreur non gérée", "<p>Le serveur a renvoyé une réponse inattendue lors du traitement de la requete.<br>Merci de signaler ce problème.</p>");
            }

            break;

        case "timeout":
            create_error_modal("Délai d'attente dépassé", "<p>Le serveur a mis trop de temps à répondre à la requete.</p><p>Vérifiez que votre équipement est toujours connecté au réseau et si tel est le cas, merci de signaler ce problème.</p>");
    }
}