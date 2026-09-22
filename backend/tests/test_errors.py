import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest

from app.database.db_errors import extract_error_entries, build_error_insights


def test_extract_error_entries_from_response():
    response = '''
    Hello! How are you?
    [Error]: "I go" -> "I went"
    [Explicacion]: Usamos el pasado cuando hablamos de una acción finalizada.
    
    [Error]: "she don't" -> "she doesn't"
    [Explicacion]: En tercera persona usamos does not don't.
    '''

    entries = extract_error_entries(response)

    assert entries == [
        {
            "wrong_form": "I go",
            "correct_form": "I went",
            "explanation": "Usamos el pasado cuando hablamos de una acción finalizada.",
            "category": "grammar",
        },
        {
            "wrong_form": "she don't",
            "correct_form": "she doesn't",
            "explanation": "En tercera persona usamos does not don't.",
            "category": "grammar",
        },
    ]


@pytest.mark.asyncio
async def test_build_error_insights_uses_model(monkeypatch):
    async def fake_model(messages):
        assert any("Resumen" in msg["content"] for msg in messages)
        return "Resumen: repites el pasado y la tercera persona. Debes practicar más verbos irregulares."

    monkeypatch.setattr("app.database.db_errors.chat_with_ollama", fake_model)

    insight = await build_error_insights([
        {"wrong_form": "I go", "correct_form": "I went", "explanation": "Pasado"},
        {"wrong_form": "she don't", "correct_form": "she doesn't", "explanation": "Tercera persona"},
    ])

    assert "repites el pasado" in insight.lower()
    assert "tercera persona" in insight.lower()
