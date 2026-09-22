from app.database.connection import get_db


async def create_session(mode: str = "conversation") -> int:
    db = await get_db()
    cursor = await db.execute(
        "INSERT INTO sessions (mode) VALUES (?)", (mode,)
    )
    await db.commit()
    session_id = cursor.lastrowid
    await db.close()
    return session_id


async def end_session(session_id: int, message_count: int):
    db = await get_db()
    await db.execute("""
        UPDATE sessions
        SET ended_at = CURRENT_TIMESTAMP, message_count = ?
        WHERE id = ?
    """, (message_count, session_id))
    await db.commit()
    await db.close()


async def save_message(session_id: int, role: str, content: str):
    db = await get_db()
    await db.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content),
    )
    await db.commit()
    await db.close()


async def get_recent_messages(session_id: int, limit: int = 20) -> list[dict]:
    db = await get_db()
    cursor = await db.execute("""
        SELECT role, content FROM messages
        WHERE session_id = ?
        ORDER BY created_at ASC
        LIMIT ?
    """, (session_id, limit))
    rows = await cursor.fetchall()
    await db.close()
    return [{"role": row["role"], "content": row["content"]} for row in rows]