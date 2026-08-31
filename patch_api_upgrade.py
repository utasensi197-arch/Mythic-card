from pathlib import Path

p = Path("web_server.py")
s = p.read_text()

# -----------------------------
# GET routes
# -----------------------------

old_get = '''        if path == "/api/stats":
            return self.stats()
'''

new_get = '''        if path == "/api/stats":
            return self.stats()

        if path == "/api/me":
            return self.me()

        if path == "/api/collection":
            return self.collection()

        if path == "/api/events":
            return self.events()

        if path == "/api/battles":
            return self.battles()

        if path == "/api/trades":
            return self.trades()

        if path == "/api/premium":
            return self.premium()
'''

if old_get not in s:
    raise SystemExit("❌ GET route anchor not found")

s = s.replace(old_get, new_get, 1)

# -----------------------------
# POST routes
# -----------------------------

old_post = '''        if path == "/api/catch":
            return self.catch_card()
'''

new_post = '''        if path == "/api/catch":
            return self.catch_card()

        if path == "/api/premium/request":
            return self.premium_request()
'''

if old_post not in s:
    raise SystemExit("❌ POST route anchor not found")

s = s.replace(old_post, new_post, 1)

# -----------------------------
# Insert API methods
# -----------------------------

anchor = '''    def cards(self):
'''

methods = r'''    def _get_authenticated_user(self):
        """
        Read Telegram initData from ?initData=...
        and return the local DB user.
        """
        query = parse_qsl(
            urlparse(self.path).query,
            keep_blank_values=True
        )

        params = dict(query)
        init_data = params.get("initData", "")

        telegram_user, error = self.verify_telegram_init_data(init_data)

        if error:
            return None, error

        telegram_id = int(telegram_user["id"])

        with get_db() as db:
            row = db.execute("""
                SELECT *
                FROM users
                WHERE telegram_id = ?
            """, (telegram_id,)).fetchone()

        if not row:
            return None, "Telegram user is not registered"

        return row, None


    def me(self):
        try:
            user, error = self._get_authenticated_user()

            if error:
                return json_response(self, {
                    "ok": False,
                    "error": error
                }, 401)

            return json_response(self, {
                "ok": True,
                "user": {
                    "id": user["id"],
                    "telegram_id": user["telegram_id"],
                    "username": user["username"],
                    "first_name": user["first_name"],
                    "is_owner": bool(user["is_owner"]),
                    "is_premium": bool(user["is_premium"]),
                    "premium_until": user["premium_until"]
                }
            })

        except Exception as e:
            return json_response(self, {
                "ok": False,
                "error": str(e)
            }, 500)


    def collection(self):
        try:
            user, error = self._get_authenticated_user()

            if error:
                return json_response(self, {
                    "ok": False,
                    "error": error
                }, 401)

            with get_db() as db:
                rows = db.execute("""
                    SELECT
                        c.id,
                        c.card_code,
                        c.name,
                        c.rarity,
                        c.image_path,
                        co.quantity,
                        co.first_obtained_at
                    FROM collections co
                    JOIN cards c ON c.id = co.card_id
                    WHERE co.user_id = ?
                    ORDER BY
                        CASE c.rarity
                            WHEN 'mythic' THEN 1
                            WHEN 'legendary' THEN 2
                            WHEN 'epic' THEN 3
                            WHEN 'rare' THEN 4
                            WHEN 'uncommon' THEN 5
                            WHEN 'common' THEN 6
                        END,
                        c.id DESC
                """, (user["id"],)).fetchall()

            return json_response(self, {
                "ok": True,
                "cards": [dict(row) for row in rows]
            })

        except Exception as e:
            return json_response(self, {
                "ok": False,
                "error": str(e)
            }, 500)


    def events(self):
        try:
            rows = []

            with get_db() as db:
                events = db.execute("""
                    SELECT
                        e.id,
                        e.name,
                        e.max_players,
                        e.status,
                        e.created_at,
                        COUNT(ep.user_id) AS players
                    FROM events e
                    LEFT JOIN event_players ep
                        ON ep.event_id = e.id
                    GROUP BY e.id
                    ORDER BY e.id DESC
                """).fetchall()

                rows = [dict(row) for row in events]

            return json_response(self, {
                "ok": True,
                "events": rows
            })

        except Exception as e:
            return json_response(self, {
                "ok": False,
                "error": str(e)
            }, 500)


    def battles(self):
        try:
            user, error = self._get_authenticated_user()

            if error:
                return json_response(self, {
                    "ok": False,
                    "error": error
                }, 401)

            with get_db() as db:
                rows = db.execute("""
                    SELECT
                        b.id,
                        b.challenger_id,
                        b.opponent_id,
                        b.challenger_card_id,
                        b.opponent_card_id,
                        b.status,
                        b.winner_user_id,
                        b.created_at
                    FROM battles b
                    WHERE b.challenger_id = ?
                       OR b.opponent_id = ?
                    ORDER BY b.id DESC
                """, (
                    user["id"],
                    user["id"]
                )).fetchall()

            return json_response(self, {
                "ok": True,
                "battles": [dict(row) for row in rows]
            })

        except Exception as e:
            return json_response(self, {
                "ok": False,
                "error": str(e)
            }, 500)


    def trades(self):
        try:
            user, error = self._get_authenticated_user()

            if error:
                return json_response(self, {
                    "ok": False,
                    "error": error
                }, 401)

            with get_db() as db:
                rows = db.execute("""
                    SELECT
                        t.id,
                        t.from_user_id,
                        t.to_user_id,
                        t.offered_card_id,
                        t.requested_card_id,
                        t.status,
                        t.created_at
                    FROM trades t
                    WHERE t.from_user_id = ?
                       OR t.to_user_id = ?
                    ORDER BY t.id DESC
                """, (
                    user["id"],
                    user["id"]
                )).fetchall()

            return json_response(self, {
                "ok": True,
                "trades": [dict(row) for row in rows]
            })

        except Exception as e:
            return json_response(self, {
                "ok": False,
                "error": str(e)
            }, 500)


    def premium(self):
        try:
            user, error = self._get_authenticated_user()

            if error:
                return json_response(self, {
                    "ok": False,
                    "error": error
                }, 401)

            with get_db() as db:
                requests = db.execute("""
                    SELECT
                        id,
                        amount_mmk,
                        requested_days,
                        status,
                        created_at,
                        processed_at
                    FROM premium_requests
                    WHERE user_id = ?
                    ORDER BY id DESC
                    LIMIT 20
                """, (user["id"],)).fetchall()

            return json_response(self, {
                "ok": True,
                "premium": {
                    "is_premium": bool(user["is_premium"]),
                    "premium_until": user["premium_until"]
                },
                "requests": [dict(row) for row in requests]
            })

        except Exception as e:
            return json_response(self, {
                "ok": False,
                "error": str(e)
            }, 500)


    def premium_request(self):
        try:
            length = int(
                self.headers.get("Content-Length", "0")
            )

            if length <= 0 or length > 100_000:
                return json_response(self, {
                    "ok": False,
                    "error": "Invalid request body"
                }, 400)

            raw = self.rfile.read(length)
            payload = json.loads(raw.decode("utf-8"))

            init_data = payload.get("initData", "")
            amount_mmk = int(payload.get("amount_mmk", 0))

            if amount_mmk <= 0:
                return json_response(self, {
                    "ok": False,
                    "error": "Invalid premium amount"
                }, 400)

            telegram_user, error = self.verify_telegram_init_data(
                init_data
            )

            if error:
                return json_response(self, {
                    "ok": False,
                    "error": error
                }, 401)

            telegram_id = int(telegram_user["id"])

            with get_db() as db:
                user = db.execute("""
                    SELECT id
                    FROM users
                    WHERE telegram_id = ?
                """, (telegram_id,)).fetchone()

                if not user:
                    return json_response(self, {
                        "ok": False,
                        "error": "User is not registered"
                    }, 401)

                cursor = db.execute("""
                    INSERT INTO premium_requests(
                        user_id,
                        amount_mmk,
                        requested_days,
                        status
                    )
                    VALUES (?, ?, NULL, 'pending')
                """, (
                    user["id"],
                    amount_mmk
                ))

                request_id = cursor.lastrowid

            return json_response(self, {
                "ok": True,
                "message": "Premium request submitted",
                "request_id": request_id
            })

        except (ValueError, TypeError):
            return json_response(self, {
                "ok": False,
                "error": "Invalid premium request"
            }, 400)

        except json.JSONDecodeError:
            return json_response(self, {
                "ok": False,
                "error": "Invalid JSON"
            }, 400)

        except Exception as e:
            return json_response(self, {
                "ok": False,
                "error": str(e)
            }, 500)


'''

if anchor not in s:
    raise SystemExit("❌ Method insertion anchor not found")

s = s.replace(anchor, methods + anchor, 1)

p.write_text(s)

print("✅ API UPGRADE PATCH APPLIED")
