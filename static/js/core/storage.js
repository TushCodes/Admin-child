(function (window) {
    "use strict";

    function appendLimited(key, value, limit) {
        limit = limit || 50;
        var values = [];
        try {
            values = JSON.parse(localStorage.getItem(key)) || [];
            values.push(value);
            if (values.length > limit) values = values.slice(-limit);
            localStorage.setItem(key, JSON.stringify(values));
        } catch (error) {
            console.error("Error saving to localStorage:", error);
        }
        return values;
    }

    function getJson(key, fallback) {
        try {
            return JSON.parse(localStorage.getItem(key)) || fallback;
        } catch (error) {
            console.error("Error reading localStorage:", error);
            return fallback;
        }
    }

    window.App = window.App || {};
    window.App.storage = { appendLimited: appendLimited, getJson: getJson };
})(window);
