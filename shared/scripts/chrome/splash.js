/*!
 * Design System SGA — chrome/splash.js
 * ------------------------------------------------------------
 * Splash screen lifecycle:
 *   data-state="in"   (rendered by build HTML)
 *   data-state="out"  (set at 1500ms → CSS fades opacity to 0)
 *   data-state="done" (set at 1900ms → CSS sets display:none)
 *
 * Bypass: any URL with ?nosplash=1 sets state="done" immediately.
 *
 * Does NOT block other init code — this runs right away and does
 * not await anything. Sections are free to initialize underneath.
 * ============================================================ */
(function () {
    'use strict';

    function dismiss(splash) {
        splash.setAttribute('data-state', 'done');
    }

    function init() {
        var splash = document.getElementById('dsSplash');
        if (!splash) return;

        // Bypass via URL param
        try {
            var params = new URLSearchParams(window.location.search);
            if (params.get('nosplash') === '1') {
                dismiss(splash);
                return;
            }
        } catch (_) { /* IE11 — ignore */ }

        // Start fade-out at 1500ms
        setTimeout(function () {
            splash.setAttribute('data-state', 'out');
        }, 1500);

        // Fully remove from tab order at 1500 + 400 = 1900ms
        setTimeout(function () {
            dismiss(splash);
        }, 1900);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
