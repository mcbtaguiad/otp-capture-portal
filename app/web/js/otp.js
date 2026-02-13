// Utility: get URL parameter by name
function getParameter(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    const regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)");
    const results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

// Prevent multiple clicks
let working = false;

// Text messages (localizable)
const messages = {
    errorTerm: "Please accept the Terms of Use before connecting.",
    errorBanner: "Error",
    registering: "Registering...",
    registeredSuccessfully: "Registered successfully!",
    errorInvalidParameter: "Invalid registration parameters.",
    errorInvalidOtp: "Invalid or expired OTP code.",
    connectButton: "Connect"
};

// Register button handler
$(document).ready(function () {
    $("#register").off("click").on("click", function (e) {
        e.preventDefault();

        // Check if Terms & Conditions are accepted
        if (!$('#agreeBox').is(':checked')) {
            showMessage("danger", `${messages.errorBanner}: ${messages.errorTerm}`);
            return;
        }

        if (working) return; // prevent double-clicks
        working = true;

        // Show loading state
        $("#register")
            .html(`<span class="fa fa-refresh fa-spin"></span> ${messages.registering}`)
            .addClass("disabled");

        // Retrieve parameters from query string
        const mac = getParameter("mac");
        const ip = getParameter("ip");
        const authaction = getParameter("authaction");
        const tok = getParameter("tok");
        const redir = getParameter("redir");
        const gatewayname = getParameter("gatewayname");

        // Get OTP if applicable
        const otp = $("#otp").val();

        // Delay for smoother UX
        setTimeout(function () {
            const url = `/register?otp=${encodeURIComponent(otp)}&mac=${encodeURIComponent(mac)}&ip=${encodeURIComponent(ip)}&tok=${encodeURIComponent(tok)}&gatewayname=${encodeURIComponent(gatewayname)}`;

            $.get(url, function (data) {
                handleResponse(data, { mac, ip, authaction, tok, redir, gatewayname });
            }).fail(function () {
                showMessage("danger", `${messages.errorBanner}: Network request failed.`);
                resetButton();
            });
        }, 1000);
    });
});

// Handle registration response
function handleResponse(data, params) {
    switch (data) {
        case "0":
            showMessage("success", `<i class="fa fa-check"></i> ${messages.registeredSuccessfully}`);
            $("#loginform").addClass("hidden");

            // Redirect after success
            const redirectUrl = `${params.authaction}?tok=${params.tok}&redir=${params.redir}&mac=${params.mac}&ip=${params.ip}&gatewayname=${params.gatewayname}`;
            window.location.href = redirectUrl;
            break;

        case "1":
            showMessage("danger", `${messages.errorBanner}: ${messages.errorInvalidParameter}`);
            resetButton();
            break;

        case "2":
            showMessage("danger", `${messages.errorBanner}: ${messages.errorInvalidOtp}`);
            resetButton();
            break;

        default:
            showMessage("danger", `${messages.errorBanner}: Unknown error (${data})`);
            resetButton();
            break;
    }
}

// Show alert message
function showMessage(type, text) {
    const messageBox = $("#message");
    messageBox.html(text).removeClass("hidden alert-danger alert-success alert-info").addClass(`alert-${type}`);
    // messageBox
    //     .html(`<i class="fa fa-exclamation-triangle"></i> ${text}`)
    //     .removeClass("hidden alert-danger alert-success alert-info")
    //     .addClass(`alert-${type}`);
}

// Reset register button
function resetButton() {
    $("#register")
        .html(messages.connectButton)
        .removeClass("disabled");
    working = false;
}