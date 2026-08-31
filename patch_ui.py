from pathlib import Path

p = Path("app/web/index.html")
s = p.read_text()

# Collection empty area
old = '''<div class="empty-card">
                    <div class="big-icon">📦</div>
                    <h3>Collection Empty</h3>
                    <p>Catch your first card to start collecting.</p>
                </div>'''

new = '''<div id="collection-empty" class="empty-card">
                    <div class="big-icon">📦</div>
                    <h3>Collection Empty</h3>
                    <p>Catch your first card to start collecting.</p>
                </div>

                <div id="collection-list" class="collection-list"></div>'''

if old not in s:
    raise SystemExit("❌ Collection anchor not found")

s = s.replace(old, new, 1)

# Add premium information to profile
old = '''<p id="profile-id">Telegram ID: —</p>
                </div>'''

new = '''<p id="profile-id">Telegram ID: —</p>
                    <div id="profile-premium" class="profile-premium">
                        Free Player
                    </div>
                    <div id="premium-status" class="premium-status">
                        FREE ACCOUNT
                    </div>
                    <div id="premium-until" class="premium-until">
                        Premium not active
                    </div>
                </div>

                <div class="section-card">
                    <h3>⭐ Premium Requests</h3>
                    <div id="premium-requests">
                        <div class="empty-mini">No requests yet.</div>
                    </div>
                </div>

                <div class="section-card">
                    <h3>⚔️ Battles</h3>
                    <div id="battles-list">
                        <div class="empty-mini">No battles yet.</div>
                    </div>
                </div>

                <div class="section-card">
                    <h3>🔄 Trades</h3>
                    <div id="trades-list">
                        <div class="empty-mini">No trades yet.</div>
                    </div>
                </div>'''

if old not in s:
    raise SystemExit("❌ Profile anchor not found")

s = s.replace(old, new, 1)

# Add events section to Drops screen
old = '''<div class="empty-card">
                    <div class="big-icon">🎴</div>
                    <h3>Active Drops</h3>
                    <p>Your available cards will appear here.</p>
                </div>'''

new = '''<div class="empty-card">
                    <div class="big-icon">🎴</div>
                    <h3>Active Drops</h3>
                    <p>Your available cards will appear here.</p>
                </div>

                <div class="section-card">
                    <h3>🏆 Events</h3>
                    <div id="events-list">
                        <div class="empty-mini">No events yet.</div>
                    </div>
                </div>'''

if old not in s:
    raise SystemExit("❌ Drops anchor not found")

s = s.replace(old, new, 1)

# Change collection total label
s = s.replace(
    '<strong id="total-cards">0</strong>',
    '<strong id="total-cards">0</strong>',
    1
)

# Add owned count hidden/helper target
s = s.replace(
    '<span>Total</span>',
    '<span>Total Cards</span>',
    1
)

p.write_text(s)

print("✅ UI HTML PATCH APPLIED")
