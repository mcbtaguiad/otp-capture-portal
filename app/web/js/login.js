let working = false;

const messages = {
    welcome_message: "Don’t share credentials with non-employees.",
    errorBanner: "Error",
    errorEmptyFields: "Please enter both username and password.",
    loggingIn: "Logging in...",
    loginSuccess: "Login successful!",
    loginFailed: "Invalid username or password.",
    connectButton: "Login"
};

$(document).ready(function () {
    $("#login").off("click").on("click", function (e) {
        e.preventDefault();
        if (working) return;
        working = true;

        const username = $("input[name='username']").val().trim();
        const password = $("input[name='password']").val().trim();

        if (!username || !password) {
            showMessage("danger", `${messages.errorBanner}: ${messages.errorEmptyFields}`);
            working = false;
            return;
        }

        $("#login")
            .html(`<span class="fa fa-refresh fa-spin"></span> ${messages.loggingIn}`)
            .addClass("disabled");

        $.ajax({
            url: "/login",
            type: "POST",
            contentType: "application/json",
            dataType: "json",
            data: JSON.stringify({ username, password }),
            success: handleResponse,
            error: function () {
                showMessage("danger", `${messages.errorBanner}: Network request failed.`);
                resetButton();
            }
        });
    });
});

function handleResponse(data) {
    if (!data || !data.status) {
        showMessage("danger", `${messages.errorBanner}: Unknown error`);
        resetButton();
        return;
    }

    if (data.status === "success") {
        showMessage("success", `<i class="fa fa-check"></i> ${data.message || messages.loginSuccess}`);
        setTimeout(() => window.location.href = data.redirect || "/dashboard", 500);
    } else {
        showMessage("danger", `<i class="fa fa-exclamation-triangle"></i> ${data.message || messages.loginFailed}`);
        resetButton();
    }
}

function showMessage(type, text) {
    const messageBox = $("#message");
    messageBox.html(text).removeClass("hidden alert-danger alert-success alert-info").addClass(`alert-${type}`);
}

function resetButton() {
    $("#login").html(messages.connectButton).removeClass("disabled");
    working = false;
}
