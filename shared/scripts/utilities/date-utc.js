/*!
 * Design System SGA — utilities/date-utc.js
 * ------------------------------------------------------------
 * UTC clock ticker used by the shell bar. Provides a single
 * setInterval that updates the headerUTC, clockDisplay and
 * headerDate elements once a second. If these elements already
 * have another updater (legacy updateHeaderClock in COE source),
 * this file is a no-op — it checks for a dsDateUtcInstalled flag
 * before installing its own ticker.
 *
 * Usage: included via {{DS_JS}} or inline before </body>.
 * ============================================================ */
(function () {
    'use strict';

    if (window.dsDateUtcInstalled) return;

    function tick() {
        var now = new Date();
        var timeLocal = now.toLocaleTimeString('pt-PT', { hour12: false });
        var timeUtc = now.toLocaleTimeString('pt-PT', { hour12: false, timeZone: 'UTC' });

        var utcEl = document.getElementById('headerUTC');
        if (utcEl) utcEl.textContent = 'UTC ' + timeUtc;

        var localEl = document.getElementById('clockDisplay');
        if (localEl) localEl.textContent = timeLocal;

        var dbClock = document.getElementById('dashboardClock');
        if (dbClock) dbClock.textContent = timeLocal;
        var dbUTC = document.getElementById('dashboardUTC');
        if (dbUTC) dbUTC.textContent = 'UTC ' + timeUtc;
    }

    // If the legacy updateHeaderClock is already installed (COE source),
    // don't double-tick — the legacy function already handles everything.
    if (typeof window.updateHeaderClock === 'function') {
        window.dsDateUtcInstalled = true;
        return;
    }

    tick();
    setInterval(tick, 1000);
    window.dsDateUtcInstalled = true;
})();
