/**
 * @file Loads the shared WhatsHelp contact widget once.
 */
(function (window, document) {
    "use strict";

    var DEFAULT_OPTIONS = {
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

    /** Loads the WhatsHelp chat button. */
    function init(options) {
        if (document.querySelector('script[data-chat-widget="whatshelp"]')) return;

        var protocol = document.location.protocol;
        var host = "whatshelp.io";
        var widgetScript = document.createElement("script");
        widgetScript.type = "text/javascript";
        widgetScript.async = true;
        widgetScript.dataset.chatWidget = "whatshelp";
        widgetScript.src = protocol + "//static." + host + "/widget-send-button/js/init.js";
        widgetScript.onload = function () {
            if (typeof window.WhWidgetSendButton !== "undefined") {
                window.WhWidgetSendButton.init(host, protocol, options || DEFAULT_OPTIONS);
            }
        };

        var firstScript = document.getElementsByTagName("script")[0];
        if (firstScript && firstScript.parentNode) {
            firstScript.parentNode.insertBefore(widgetScript, firstScript);
        }
    }

    window.App = window.App || {};
    window.App.chatWidget = { init: init };
})(window, document);
