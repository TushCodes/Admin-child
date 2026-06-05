/**
 * @file Runs warehousing-page interactions and chat widget setup.
 */
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("form").forEach(function (form) {
        form.addEventListener("submit", function (event) {
            var hasError = false;
            form.querySelectorAll("[required]").forEach(function (field) {
                if (!field.value.trim()) {
                    field.classList.add("is-invalid");
                    hasError = true;
                } else {
                    field.classList.remove("is-invalid");
                }
            });
            if (hasError) {
                event.preventDefault();
            }
        });
    });

    
});

(function () {
    var options = {
        whatsapp: "+91-9910417643",
        email: "info@gramsec.com",
        sms: "+91-9910417643",
        call: "+91-9910417643",
        company_logo_url: "https://www.gramscs.com/images/logo.jpg",
        greeting_message: "Connect with Gram Experts. Connect with us for any assistance.",
        call_to_action: "Connect with us",
        button_color: "#E74339",
        position: "left",
        order: "whatsapp,sms,call,email"
    };

    var protocol = document.location.protocol;
    var host = "whatshelp.io";
    var url = protocol + "//static." + host;
    var widgetScript = document.createElement("script");
    widgetScript.type = "text/javascript";
    widgetScript.async = true;
    widgetScript.src = url + "/widget-send-button/js/init.js";
    widgetScript.onload = function () {
        if (typeof WhWidgetSendButton !== "undefined") {
            WhWidgetSendButton.init(host, protocol, options);
        }
    };

    var firstScript = document.getElementsByTagName("script")[0];
    if (firstScript && firstScript.parentNode) {
        firstScript.parentNode.insertBefore(widgetScript, firstScript);
    }
})();
