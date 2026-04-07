import json
import os
import sqlite3
from datetime import datetime, timezone


class LocalCacheRepository:
    """Stores aggregated app snapshots in a local SQLite database."""

    def __init__(self, db_path=None):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.db_path = db_path or os.path.join(base_dir, "context", "acua_cache.db")
        self._ensure_db()

    def _ensure_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS snapshots (
                    subscription_id TEXT NOT NULL,
                    rg_key TEXT NOT NULL,
                    rg_json TEXT NOT NULL,
                    cost_json TEXT NOT NULL,
                    usage_json TEXT NOT NULL,
                    is_mock INTEGER NOT NULL DEFAULT 0,
                    refreshed_at TEXT NOT NULL,
                    PRIMARY KEY (subscription_id, rg_key)
                )
                """
            )

    @staticmethod
    def _rg_key(resource_groups):
        ordered = sorted(resource_groups)
        return "||".join(ordered)

    def save_snapshot(self, subscription_id, resource_groups, cost_summary, usage_summary):
        rg_key = self._rg_key(resource_groups)
        refreshed_at = datetime.now(timezone.utc).isoformat()
        is_mock = int(bool(cost_summary.get("is_mock") or usage_summary.get("is_mock")))

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO snapshots (
                    subscription_id, rg_key, rg_json, cost_json, usage_json, is_mock, refreshed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(subscription_id, rg_key) DO UPDATE SET
                    rg_json=excluded.rg_json,
                    cost_json=excluded.cost_json,
                    usage_json=excluded.usage_json,
                    is_mock=excluded.is_mock,
                    refreshed_at=excluded.refreshed_at
                """,
                (
                    subscription_id,
                    rg_key,
                    json.dumps(sorted(resource_groups)),
                    json.dumps(cost_summary),
                    json.dumps(usage_summary),
                    is_mock,
                    refreshed_at,
                ),
            )

    def get_snapshot(self, subscription_id, resource_groups):
        rg_key = self._rg_key(resource_groups)
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT rg_json, cost_json, usage_json, is_mock, refreshed_at
                FROM snapshots
                WHERE subscription_id = ? AND rg_key = ?
                """,
                (subscription_id, rg_key),
            ).fetchone()

        if not row:
            return None

        rg_json, cost_json, usage_json, is_mock, refreshed_at = row
        return {
            "resource_groups": json.loads(rg_json),
            "cost_summary": json.loads(cost_json),
            "usage_summary": json.loads(usage_json),
            "is_mock": bool(is_mock),
            "refreshed_at": refreshed_at,
        }
