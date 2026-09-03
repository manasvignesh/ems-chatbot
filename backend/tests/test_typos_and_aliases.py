from app.ai.query_analysis import query_analyzer


def test_normalize_equinox_typos():
    typo_queries = [
        ("equniox", "equinox-2.0"),
        ("spotlite", "spotlight"),
        ("cross road", "crossroads"),
        ("crossraods", "crossroads"),
        ("start up expo", "startup-expo"),
        ("brand batles", "brand-battles"),
        ("ipl action", "ipl-auction"),
        ("hustle maniya", "hustle-mania"),
        ("intership drive", "internship-drive"),
        ("startup polly", "startup-poly"),
        ("ecell meet", "e-cell-meet"),
        ("pitchdeck", "pitch-deck"),
    ]
    for q, expected_id in typo_queries:
        analysis = query_analyzer.analyze(q)
        assert analysis.matched_event_id == expected_id, f"Query '{q}' failed to match '{expected_id}', got '{analysis.matched_event_id}'"


def test_semantic_descriptions():
    desc_queries = [
        ("monopoly event", "startup-poly"),
        ("cricket bidding", "ipl-auction"),
        ("pitch to investors", "pitch-deck"),
        ("sell products", "hustle-mania"),
    ]
    for q, expected_id in desc_queries:
        analysis = query_analyzer.analyze(q)
        assert analysis.matched_event_id == expected_id, f"Query '{q}' failed to match '{expected_id}', got '{analysis.matched_event_id}'"
