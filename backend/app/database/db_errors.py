from app.database.connection import get_db


async def register_error(
    wrong_form: str,
    correct_form: str,
    explanation: str = "",
    category: str = "general",
):
    db = await get_db()

    cursor = await db.execute(
        "SELECT id, frequency FROM errors WHERE wrong_form = ?",
        (wrong_form,),
    )
    existing = await cursor.fetchone()

    if existing:
        await db.execute("""
            UPDATE errors
            SET frequency = frequency + 1,
                last_seen = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (existing["id"],))
    else:
        await db.execute("""
            INSERT INTO errors (category, wrong_form, correct_form, explanation)
            VALUES (?, ?, ?, ?)
        """, (category, wrong_form, correct_form, explanation))

    await db.commit()
    await db.close()


async def get_top_errors(limit: int = 10) -> list[dict]:
    db = await get_db()
    cursor = await db.execute("""
        SELECT category, wrong_form, correct_form, explanation, frequency
        FROM errors
        ORDER BY frequency DESC
        LIMIT ?
    """, (limit,))
    rows = await cursor.fetchall()
    await db.close()
    return [dict(row) for row in rows]


async def get_errors_summary() -> list[dict]:
    db = await get_db()
    cursor = await db.execute("""
        SELECT category, COUNT(*) as error_count, SUM(frequency) as total_occurrences
        FROM errors
        GROUP BY category
        ORDER BY total_occurrences DESC
    """)
    rows = await cursor.fetchall()
    await db.close()
    return [dict(row) for row in rows]