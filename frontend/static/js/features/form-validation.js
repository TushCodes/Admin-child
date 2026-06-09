/**
 * @file Shared form checks.
 */
(function (window, document) {
    "use strict";

    /** Marks required fields that are empty. */
    function markRequiredFields(form) {
        var hasError = false;
        form.querySelectorAll("[required]").forEach(function (field) {
            var isEmpty = !String(field.value || "").trim();
            field.classList.toggle("is-invalid", isEmpty);
            if (isEmpty) hasError = true;
        });
        return !hasError;
    }

    /** Skips forms that have their own checks. */
    function shouldSkip(form) {
        return form.id === "contactForm" || form.hasAttribute("data-skip-shared-validation");
    }

    /** Stops submit when form is invalid. */
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

    /** Starts validation for normal forms. */
    function init() {
        document.querySelectorAll("form").forEach(bind);
    }

    window.App = window.App || {};
    window.App.formValidation = { init: init, markRequiredFields: markRequiredFields };
})(window, document);
