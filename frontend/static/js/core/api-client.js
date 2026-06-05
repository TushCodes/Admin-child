/**
 * @file Wraps fetch calls so frontend features handle JSON and errors consistently.
 */
(function (window) {
    "use strict";

    var DEFAULT_TIMEOUT = 15000;

    function joinUrl(baseUrl, path) {
        if (!baseUrl) return path;
        return baseUrl.replace(/\/$/, "") + "/" + String(path || "").replace(/^\//, "");
    }

    function request(path, options) {
        options = options || {};
        var timeout = typeof options.timeout === "number" ? options.timeout : DEFAULT_TIMEOUT;
        var controller = new AbortController();
        var timer = setTimeout(function () { controller.abort(); }, timeout);
        var baseUrl = window.APP_CONFIG && window.APP_CONFIG.apiBaseUrl ? window.APP_CONFIG.apiBaseUrl : "";
        var fetchOptions = Object.assign(
            { credentials: "include" },
            options,
            { signal: controller.signal }
        );

        return fetch(joinUrl(baseUrl, path), fetchOptions).finally(function () {
            clearTimeout(timer);
        });
    }

    window.App = window.App || {};
    window.App.apiClient = { request: request };
})(window);
