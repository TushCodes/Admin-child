/**
 * @file Provides shared hash popup lifecycle and scroll-lock behavior.
 */
(function (window, document) {
    "use strict";

    function getTargetPopup(selector) {
        var hash = window.location.hash;
        if (!hash) return null;
        try {
            var target = document.querySelector(hash);
            return target && target.matches(selector) ? target : null;
        } catch (error) {
            return null;
        }
    }

    function setScrollLocked(isLocked) {
        document.body.style.overflow = isLocked ? "hidden" : "";
    }

    function close(closeHash) {
        if (closeHash) {
            window.location.hash = closeHash;
            return;
        }
        if (window.history && window.history.pushState) {
            window.history.pushState("", document.title, window.location.pathname + window.location.search);
            var hashEvent;
            if (typeof window.HashChangeEvent === "function") {
                hashEvent = new HashChangeEvent("hashchange");
            } else {
                hashEvent = document.createEvent("Event");
                hashEvent.initEvent("hashchange", true, true);
            }
            window.dispatchEvent(hashEvent);
            return;
        }
        window.location.hash = "";
    }

    function init(options) {
        options = options || {};
        var selector = options.selector || ".pop-overlay";
        var closeHash = options.closeHash || document.body.getAttribute("data-popup-close-hash") || "";

        function isOpen() {
            return !!getTargetPopup(selector);
        }

        function syncScroll() {
            setScrollLocked(isOpen());
        }

        document.querySelectorAll(selector).forEach(function (overlay) {
            overlay.addEventListener("click", function (event) {
                if (event.target === overlay) close(closeHash);
            });
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape" && isOpen()) close(closeHash);
        });

        window.addEventListener("hashchange", syncScroll);
        syncScroll();
    }

    window.App = window.App || {};
    window.App.popupManager = { init: init, close: close };
})(window, document);
