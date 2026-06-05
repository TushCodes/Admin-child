/**
 * @file Coordinates about-page gallery links, contact messages, and chat widget setup.
 */
document.addEventListener("DOMContentLoaded", function () {
    function isPopupOpen() {
        return window.location.hash.startsWith("#gal");
    }

    function closeAllPopups() {
        window.location.hash = "";
    }

    function toggleBodyScroll(disable) {
        document.body.style.overflow = disable ? "hidden" : "";
    }

    window.addEventListener("hashchange", function () {
        toggleBodyScroll(isPopupOpen());
    });
    toggleBodyScroll(isPopupOpen());

    document.querySelectorAll(".pop-overlay").forEach(function (overlay) {
        overlay.addEventListener("click", function (event) {
            if (event.target === overlay) {
                closeAllPopups();
            }
        });
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && isPopupOpen()) {
            closeAllPopups();
        }
    });

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

    window.showToast = function (message, type) {
        var toastType = type || "success";
        var toastContainer = document.getElementById("toast-container");
        if (!toastContainer) {
            return;
        }

        var toast = document.createElement("div");
        toast.className = "toast toast-" + toastType;
        toast.style.minWidth = "250px";
        toast.style.backgroundColor = toastType === "success" ? "#82CF2B" : "#dc3545";
        toast.style.color = "white";
        toast.style.padding = "15px 20px";
        toast.style.marginBottom = "10px";
        toast.style.borderRadius = "4px";
        toast.style.boxShadow = "0 4px 8px rgba(0,0,0,0.1)";
        toast.style.opacity = "0";
        toast.style.transition = "opacity 0.3s ease-in-out";
        toast.innerHTML =
            '<div class="d-flex align-items-center">' +
            '<span class="fa fa-' + (toastType === "success" ? "check-circle" : "exclamation-circle") + ' me-2"></span>' +
            "<div>" + message + "</div>" +
            "</div>";

        toastContainer.appendChild(toast);

        setTimeout(function () {
            toast.style.opacity = "1";
        }, 10);

        setTimeout(function () {
            toast.style.opacity = "0";
            setTimeout(function () {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    };

    
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
