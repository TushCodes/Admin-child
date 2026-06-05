/**
 * @file Adds browser-side feedback and submission behavior to contact forms.
 */
(function (window, document) {
    "use strict";

    var REQUIRED_FIELDS = ["name", "email", "phone", "subject", "message"];

    function toObject(formData) {
        var formObject = {};
        formData.forEach(function (value, key) { formObject[key] = value; });
        formObject.timestamp = new Date().toISOString();
        return formObject;
    }

    function validate(formData) {
        for (var i = 0; i < REQUIRED_FIELDS.length; i += 1) {
            var field = REQUIRED_FIELDS[i];
            if (!formData[field] || String(formData[field]).trim().length === 0) return false;
        }
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) return false;
        return /[\d+\-() ]{7,20}/.test(formData.phone);
    }

    function setLoading(form, isLoading, originalText) {
        var submitButton = form.querySelector('button[type="submit"]');
        if (!submitButton) return "";
        var textNode = submitButton.querySelector(".btn-text");
        var currentText = textNode ? textNode.textContent : submitButton.textContent;
        if (textNode) textNode.textContent = isLoading ? "Sending..." : originalText;
        else submitButton.textContent = isLoading ? "Sending..." : originalText;
        submitButton.disabled = isLoading;
        return currentText;
    }

    function bind(form) {
        form.addEventListener("submit", function (event) {
            event.preventDefault();
            var formData = new FormData(form);
            var formObject = toObject(formData);
            if (!validate(formObject)) {
                window.App.toast.show("Please fill in all required fields correctly.", "error");
                return;
            }

            var originalText = setLoading(form, true);
            window.App.storage.appendLimited("contactSubmissions", formObject, 50);

            window.App.apiClient.request(form.getAttribute("action") || "/contact", {
                method: "POST",
                body: formData,
                headers: { "X-Requested-With": "XMLHttpRequest" }
            }).then(function (response) {
                if (response.ok) {
                    window.App.toast.show("Thank you! Your message has been received.", "success");
                    form.reset();
                    return;
                }
                window.App.toast.show("Saved locally — server unavailable.", "error");
            }).catch(function (error) {
                console.error("Contact submission failed:", error);
                window.App.toast.show("Saved locally — server unavailable.", "error");
                form.reset();
            }).finally(function () {
                setLoading(form, false, originalText);
            });
        });
    }

    function init() {
        var form = document.getElementById("contactForm");
        if (form) bind(form);
    }

    window.App = window.App || {};
    window.App.contactForm = { init: init, validate: validate };
})(window, document);
