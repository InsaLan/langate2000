// "New User" modal event listeners

$('#create_account_role').change(function () {
    if ($("#create_account_role").val() === "player") {
        $("#create_account_payment_g").show();
        $("#create_account_tournament_g").show();
    }
    else {
        $("#create_account_payment_g").hide();
        $("#create_account_tournament_g").hide();
    }
});
