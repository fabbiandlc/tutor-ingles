import re

from app.database.connection import get_db
from app.services.ollama_service import chat_with_ollama


def extract_error_entries(response: str) -> list[dict]:
    entries: list[dict] = []
    lines = (response or "").splitlines()
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if not line.lower().startswith("[error]:"):
            i += 1
            continue

        match = re.search(r'"(.*?)"\s*->\s*"(.*?)"', line, re.DOTALL)
        if not match:
            i += 1
            continue

        wrong_form = match.group(1).strip()
        correct_form = match.group(2).strip()
        explanation = ""
        j = i + 1

        while j < len(lines):
            candidate = lines[j].strip()
            if candidate.lower().startswith("[explicacion]:"):
                explanation = candidate.split(":", 1)[1].strip()
                break
            if candidate.lower().startswith("[error]:"):
                break
            j += 1

        entries.append({
            "wrong_form": wrong_form,
            "correct_form": correct_form,
            "explanation": explanation,
            "category": "grammar",
        })

        i = j + 1 if explanation else i + 1

    return entries


async def save_response_errors(response: str) -> list[dict]:
    entries = extract_error_entries(response)
    for entry in entries:
        wrong_form = (entry.get("wrong_form") or "").strip()
        correct_form = (entry.get("correct_form") or "").strip()
        if not wrong_form or not correct_form or wrong_form == correct_form:
            continue
        await register_error(
            wrong_form=wrong_form,
            correct_form=correct_form,
            explanation=(entry.get("explanation") or "").strip(),
            category=(entry.get("category") or "grammar"),
        )
    return entries


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


async def build_error_insights(errors: list[dict]) -> str:
    if not errors:
        return "Todavía no tienes errores registrados. Sigue practicando y el tutor te irá señalando patrones para trabajar."

    error_lines = []
    for item in errors[:10]:
        wrong = (item.get("wrong_form") or "").strip()
        correct = (item.get("correct_form") or "").strip()
        explanation = (item.get("explanation") or "").strip()
        if wrong and correct:
            error_lines.append(f'- "{wrong}" -> "{correct}". {explanation}'.strip())

    prompt = [
        {
            "role": "system",
            "content": "Eres un tutor de inglés para un estudiante hispanohablante. Analiza los errores mostrados y responde en español con un resumen claro, tres ideas de mejora y una recomendación de práctica."
        },
        {
            "role": "user",
            "content": "Resumen de errores:\n" + "\n".join(error_lines) + "\n\nNecesito un resumen breve y una guía práctica para mejorar."
        },
    ]

    summary = await chat_with_ollama(prompt)
    return summary.strip() or "Todavía no hay suficiente información para generar un resumen útil."
