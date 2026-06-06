/**
 * @file Adds shared browser-side validation feedback for unmanaged forms.
 */
(function (window, document) {
    "use strict";

    function markRequiredFields(form) {
        var hasError = false;
        form.querySelectorAll("[required]").forEach(function (field) {
            var isEmpty = !String(field.value || "").trim();
            field.classList.toggle("is-invalid", isEmpty);
            if (isEmpty) hasError = true;
        });
        return !hasError;
    }

    function shouldSkip(form) {
        return form.id === "contactForm" || form.hasAttribute("data-skip-shared-validation");
    }

    function bind(form) {
        form.addEventListener("submit", function (event) {
            if (shouldSkip(form)) return;

            var requiredFieldsValid = markRequiredFields(form);
            var nativeValid = typeof form.checkValidity === "function" ? form.checkValidity() : true;
            if (!requiredFieldsValid || !nativeValid) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add("was-validated");
        }, false);
    }

    function init() {
        document.querySelectorAll("form").forEach(bind);
    }

    window.App = window.App || {};
    window.App.formValidation = { init: init, markRequiredFields: markRequiredFields };
})(window, document);
