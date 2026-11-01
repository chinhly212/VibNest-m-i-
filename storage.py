from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ChatStore:
    """Small SQLite-backed store for local conversation history."""

    def __init__(self, db_path: str) -> None:
        self.db_path = str(Path(db_path))
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    messages_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute("CREATE INDEX IF NOT EXISTS idx_chats_updated ON chats(updated_at DESC)")

    def save_chat(
        self,
        chat_id: int | None,
        title: str,
        provider: str,
        model: str,
        messages: list[dict[str, str]],
    ) -> int:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        serialized = json.dumps(messages, ensure_ascii=False)
        with self._connect() as connection:
            if chat_id is None:
                cursor = connection.execute(
                    """INSERT INTO chats (title, provider, model, messages_json, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (title, provider, model, serialized, now, now),
                )
                return int(cursor.lastrowid)
            connection.execute(
                """UPDATE chats SET title=?, provider=?, model=?, messages_json=?, updated_at=? WHERE id=?""",
                (title, provider, model, serialized, now, chat_id),
            )
            return chat_id

    def list_chats(self, limit: int = 30) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, title, provider, model, updated_at FROM chats ORDER BY updated_at DESC LIMIT ?",
                (max(1, min(int(limit), 100)),),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_chat(self, chat_id: int) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM chats WHERE id=?", (chat_id,)).fetchone()
        if row is None:
            return None
        result = dict(row)
        try:
            result["messages"] = json.loads(result.pop("messages_json"))
        except (json.JSONDecodeError, TypeError):
            result["messages"] = []
        return result
