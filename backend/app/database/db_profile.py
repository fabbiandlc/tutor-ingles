from app.database.connection import get_db


async def get_profile() -> dict:
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM student_profile WHERE id = 1"
    )
    row = await cursor.fetchone()
    await db.close()
    if row:
        return dict(row)
    return {}


async def get_stats() -> dict:
    db = await get_db()

    cursor = await db.execute("SELECT COUNT(*) as total FROM sessions")
    row = await cursor.fetchone()
    total_sessions = row["total"] if row else 0

    cursor = await db.execute("SELECT COUNT(*) as total FROM messages WHERE role = 'user'")
    row = await cursor.fetchone()
    total_messages = row["total"] if row else 0

    cursor = await db.execute("SELECT COUNT(*) as total FROM errors")
    row = await cursor.fetchone()
    total_errors = row["total"] if row else 0

    await db.close()
    return {
        "total_sessions": total_sessions,
        "total_messages": total_messages,
        "total_error_types": total_errors,
    }