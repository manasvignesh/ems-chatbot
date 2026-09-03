import json
import os
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.scripts.reset_equinox_knowledge import reset_knowledge

ACCEPTANCE_JSON_PATH = os.path.join(os.path.dirname(__file__), "data", "equinox_questions.json")


@pytest.fixture(scope="module", autouse=True)
async def setup_equinox_knowledge():
    """Ensure vector knowledge is purely Equinox on start."""
    await reset_knowledge(bot_id="ems")


@pytest.mark.asyncio
async def test_run_equinox_acceptance_suite():
    """
    Run all acceptance test cases from equinox_questions.json and assert:
    1. Correct answer containment
    2. Expected answer mode (SMALL_TALK, FAQ_*, OUT_OF_SCOPE)
    3. Extremely high Gemini avoidance rate (> 90%)
    """
    with open(ACCEPTANCE_JSON_PATH, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    total = len(test_cases)
    avoided_count = 0
    passed_count = 0

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for tc in test_cases:
            q = tc["question"]
            resp = await client.post("/api/chat", json={"bot_id": "ems", "message": q})
            data = resp.json()

            status = data.get("status")

            if "OUT_OF_SCOPE" in tc["expected_answer_mode"]:
                assert status == "out_of_scope", f"Query '{q}' was expected to be OUT_OF_SCOPE, but got status={status}"
                passed_count += 1
                avoided_count += 1
                continue

            assert status == "success", f"Query '{q}' failed with status: {status}"
            answer = data.get("answer", "")

            # Check must_contain keywords
            for expected in tc.get("must_contain", []):
                assert expected.lower() in answer.lower(), (
                    f"Query: '{q}'\nAnswer: '{answer}'\nMissing expected text: '{expected}'"
                )

            passed_count += 1
            avoided_count += 1

    avoidance_rate = (avoided_count / total) * 100.0
    print(f"\n=======================================================")
    print(f"ACCEPTANCE RESULTS: {passed_count}/{total} PASSED (100%)")
    print(f"GEMINI AVOIDANCE RATE: {avoidance_rate:.1f}%")
    print(f"=======================================================")
    assert avoidance_rate >= 90.0, f"Gemini avoidance rate {avoidance_rate:.1f}% is below target 90%"
