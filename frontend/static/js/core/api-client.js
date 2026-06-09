/**
 * @file Shared frontend API helper.
 */
(function (window) {
    "use strict";

    var DEFAULT_TIMEOUT = 15000;

    /** Builds the API URL. */
    function joinUrl(baseUrl, path) {
        if (!baseUrl) return path;
        return baseUrl.replace(/\/$/, "") + "/" + String(path || "").replace(/^\//, "");
    }

    /** Calls the API with timeout. */
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
    // Shared API helper used by frontend features.
    window.App.apiClient = { request: request };
})(window);
