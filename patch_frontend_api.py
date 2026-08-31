from pathlib import Path

p = Path("app/web/app.js")
s = p.read_text()

# Keep existing Telegram/drop/catch logic, but add authenticated API helpers
anchor = "/* -----------------------------\n   Navigation\n----------------------------- */"

if anchor not in s:
    raise SystemExit("❌ Navigation anchor not found")

methods = r'''
/* -----------------------------
   Authenticated API
----------------------------- */

function getInitData() {
    return tg?.initData || "";
}

async function apiFetch(path, options = {}) {
    const initData = getInitData();

    const headers = {
        ...(options.headers || {})
    };

    if (initData) {
        headers["X-Telegram-Init-Data"] = initData;
    }

    const response = await fetch(path, {
        cache: "no-store",
        ...options,
        headers
    });

    const data = await response.json();

    if (!response.ok || !data.ok) {
        throw new Error(data.error || `API error ${response.status}`);
    }

    return data;
}


/* -----------------------------
   Profile API
----------------------------- */

async function loadMe() {
    try {
        const data = await apiFetch("/api/me");

        const u = data.user || {};

        const name =
            u.first_name ||
            u.username ||
            "Player";

        setText("user-name", name);
        setText("profile-name", name);
        setText(
            "profile-id",
            u.telegram_id
                ? `Telegram ID: ${u.telegram_id}`
                : "Telegram ID: —"
        );

        const premiumEl =
            document.getElementById("profile-premium");

        if (premiumEl) {
            premiumEl.textContent =
                u.is_premium
                    ? `⭐ Premium until ${u.premium_until || "—"}`
                    : "Free Player";
        }

    } catch (error) {
        console.error("Me API:", error);
    }
}


/* -----------------------------
   Collection API
----------------------------- */

async function loadCollection() {
    try {
        const data = await apiFetch("/api/collection");

        const cards = data.cards || [];

        const list =
            document.getElementById("collection-list");

        const empty =
            document.getElementById("collection-empty");

        if (!list) return;

        list.innerHTML = "";

        if (!cards.length) {
            if (empty) empty.style.display = "block";
            return;
        }

        if (empty) empty.style.display = "none";

        for (const card of cards) {
            const item = document.createElement("div");
            item.className = "collection-item";

            const image = card.image_path
                ? `<img src="/${card.image_path}" alt="">`
                : `<div class="collection-placeholder">🃏</div>`;

            item.innerHTML = `
                <div class="collection-image">
                    ${image}
                </div>
                <div class="collection-info">
                    <strong>${card.name || card.card_code || "Card"}</strong>
                    <span>${String(card.rarity || "").toUpperCase()}</span>
                    <small>×${card.quantity || 0}</small>
                </div>
            `;

            list.appendChild(item);
        }

        setText("total-owned", cards.length);

    } catch (error) {
        console.error("Collection API:", error);
    }
}


/* -----------------------------
   Premium API
----------------------------- */

async function loadPremium() {
    try {
        const data = await apiFetch("/api/premium");

        const premium = data.premium || {};
        const requests = data.requests || [];

        const status =
            document.getElementById("premium-status");

        if (status) {
            status.textContent =
                premium.is_premium
                    ? `⭐ PREMIUM ACTIVE`
                    : `FREE ACCOUNT`;
        }

        const until =
            document.getElementById("premium-until");

        if (until) {
            until.textContent =
                premium.is_premium
                    ? `Until: ${premium.premium_until || "—"}`
                    : "Premium not active";
        }

        const requestList =
            document.getElementById("premium-requests");

        if (requestList) {
            requestList.innerHTML = "";

            for (const request of requests) {
                const item = document.createElement("div");
                item.className = "premium-request";

                item.innerHTML = `
                    <strong>#${request.id}</strong>
                    <span>${request.amount_mmk || 0} MMK</span>
                    <small>${request.status || "pending"}</small>
                `;

                requestList.appendChild(item);
            }
        }

    } catch (error) {
        console.error("Premium API:", error);
    }
}


/* -----------------------------
   Events API
----------------------------- */

async function loadEvents() {
    try {
        const data = await fetch("/api/events", {
            cache: "no-store"
        }).then(r => r.json());

        if (!data.ok) {
            throw new Error(data.error || "Events API error");
        }

        const list =
            document.getElementById("events-list");

        if (!list) return;

        list.innerHTML = "";

        const events = data.events || [];

        if (!events.length) {
            list.innerHTML =
                '<div class="empty-mini">No events yet.</div>';
            return;
        }

        for (const event of events) {
            const item = document.createElement("div");
            item.className = "event-item";

            item.innerHTML = `
                <strong>${event.name || "Event"}</strong>
                <span>${event.players || 0}/${event.max_players || 0} players</span>
                <small>${event.status || ""}</small>
            `;

            list.appendChild(item);
        }

    } catch (error) {
        console.error("Events API:", error);
    }
}


/* -----------------------------
   Battles API
----------------------------- */

async function loadBattles() {
    try {
        const data = await apiFetch("/api/battles");

        const list =
            document.getElementById("battles-list");

        if (!list) return;

        list.innerHTML = "";

        const battles = data.battles || [];

        if (!battles.length) {
            list.innerHTML =
                '<div class="empty-mini">No battles yet.</div>';
            return;
        }

        for (const battle of battles) {
            const item = document.createElement("div");
            item.className = "battle-item";

            item.innerHTML = `
                <strong>Battle #${battle.id}</strong>
                <span>${battle.status || "unknown"}</span>
                <small>Winner: ${battle.winner_user_id || "—"}</small>
            `;

            list.appendChild(item);
        }

    } catch (error) {
        console.error("Battles API:", error);
    }
}


/* -----------------------------
   Trades API
----------------------------- */

async function loadTrades() {
    try {
        const data = await apiFetch("/api/trades");

        const list =
            document.getElementById("trades-list");

        if (!list) return;

        list.innerHTML = "";

        const trades = data.trades || [];

        if (!trades.length) {
            list.innerHTML =
                '<div class="empty-mini">No trades yet.</div>';
            return;
        }

        for (const trade of trades) {
            const item = document.createElement("div");
            item.className = "trade-item";

            item.innerHTML = `
                <strong>Trade #${trade.id}</strong>
                <span>${trade.status || "unknown"}</span>
                <small>${trade.created_at || ""}</small>
            `;

            list.appendChild(item);
        }

    } catch (error) {
        console.error("Trades API:", error);
    }
}


/* -----------------------------
   Dashboard refresh
----------------------------- */

async function loadUserData() {
    if (!getInitData()) {
        console.warn(
            "Telegram initData unavailable. Open from Telegram."
        );
        return;
    }

    await Promise.allSettled([
        loadMe(),
        loadCollection(),
        loadPremium(),
        loadBattles(),
        loadTrades()
    ]);
}

'''

s = s.replace(anchor, methods + "\n" + anchor, 1)

# Add authenticated user data to startup
old = """loadTelegramUser();
loadDrop();
loadStats();
loadCards();"""

new = """loadTelegramUser();
loadDrop();
loadStats();
loadCards();
loadUserData();
loadEvents();"""

if old not in s:
    raise SystemExit("❌ Startup anchor not found")

s = s.replace(old, new, 1)

# Refresh user data periodically
old2 = """setInterval(() => {
    loadDrop();
    loadStats();
}, 10000);"""

new2 = """setInterval(() => {
    loadDrop();
    loadStats();
    loadUserData();
}, 10000);"""

if old2 not in s:
    raise SystemExit("❌ Refresh anchor not found")

s = s.replace(old2, new2, 1)

p.write_text(s)

print("✅ FRONTEND API PATCH APPLIED")
