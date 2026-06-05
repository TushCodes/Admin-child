/**
 * @file Bootstraps shared frontend modules after the page loads.
 */
document.addEventListener("DOMContentLoaded", function () {
    if (window.App && window.App.contactForm) {
        window.App.contactForm.init();
    }
});

window.viewStoredSubmissions = function () {
    var submissions = window.App && window.App.storage
        ? window.App.storage.getJson("contactSubmissions", [])
        : [];
    console.table(submissions);
    return submissions;
};
