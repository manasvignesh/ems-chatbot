import asyncio
import json
import sys
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.scripts.reset_equinox_knowledge import reset_knowledge

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    await reset_knowledge("ems")
    with open("backend/tests/data/equinox_questions.json", "r", encoding="utf-8") as f:
        tcs = json.load(f)

    failures = []
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for i, tc in enumerate(tcs):
            q = tc["question"]
            resp = await client.post("/api/chat", json={"bot_id": "ems", "message": q})
            data = resp.json()
            status = data.get("status")

            if "OUT_OF_SCOPE" in tc["expected_answer_mode"]:
                if status != "out_of_scope":
                    failures.append((i, q, f"expected out_of_scope got {status}"))
                continue

            if status != "success":
                failures.append((i, q, f"status={status}, msg={data}"))
                continue

            answer = data.get("answer", "")
            for exp in tc.get("must_contain", []):
                if exp.lower() not in answer.lower():
                    failures.append((i, q, f"missing expected text '{exp}', answer was: '{answer}'"))
                    break

    print("\n================== FAILURES LIST ==================")
    for f in failures:
        print(f"#{f[0]} Q: {f[1]} -> Error: {f[2]}")
    print(f"===================================================\nTotal failures: {len(failures)}")

if __name__ == "__main__":
    asyncio.run(main())
