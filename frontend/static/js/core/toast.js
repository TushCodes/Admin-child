/**
 * @file Shows temporary success and error messages on the page.
 */
(function (window, document) {
    "use strict";

    /** Shows a small message popup. */
    function show(message, type) {
        type = type || "info";
        document.querySelectorAll(".toast-notification").forEach(function (toast) {
            toast.remove();
        });

        var toast = document.createElement("div");
        toast.className = "toast-notification toast-" + type;
        toast.innerHTML = [
            '<div class="toast-content">',
            '<div class="toast-icon">' + (type === "success" ? "✓" : type === "error" ? "✗" : "ℹ") + "</div>",
            '<div class="toast-message"></div>',
            '<button class="toast-close" type="button" aria-label="Close notification">×</button>',
            "</div>"
        ].join("");
        toast.querySelector(".toast-message").textContent = message;
        toast.querySelector(".toast-close").addEventListener("click", function () {
            toast.remove();
        });

        document.body.appendChild(toast);
        setTimeout(function () { toast.classList.add("toast-show"); }, 100);
        setTimeout(function () {
            if (toast.parentElement) {
                toast.classList.remove("toast-show");
                setTimeout(function () { toast.remove(); }, 300);
            }
        }, 5000);
    }

    window.App = window.App || {};
    window.App.toast = { show: show };
    window.showToast = show;
})(window, document);
