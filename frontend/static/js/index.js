/**
 * @file Starts shared frontend code.
 */
document.addEventListener("DOMContentLoaded", function () {
    if (window.App && window.App.popupManager) {
        window.App.popupManager.init();
    }
    if (window.App && window.App.formValidation) {
        window.App.formValidation.init();
    }
    if (window.App && window.App.contactForm) {
        window.App.contactForm.init();
    }
    if (window.App && window.App.chatWidget && document.body.hasAttribute("data-enable-chat-widget")) {
        window.App.chatWidget.init();
    }
});

/** Console helper to view saved contact forms. */
window.viewStoredSubmissions = function () {
    var submissions = window.App && window.App.storage
        ? window.App.storage.getJson("contactSubmissions", [])
        : [];
    console.table(submissions);
    return submissions;
};
