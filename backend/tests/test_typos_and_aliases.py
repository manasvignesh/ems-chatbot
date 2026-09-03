import pytest
from app.ai.query_analysis import query_analyzer


def test_normalize_gen_ai_typos():
    typo_queries = [
        "gen ai",
        "genai",
        "genarative ai",
        "generativ ai",
        "genrative ai",
        "generative artificial intelligence",
    ]
    for q in typo_queries:
        analysis = query_analyzer.analyze(q)
        assert "generative ai" in analysis.topics, f"Failed to detect Gen AI topic in: {q}"
        assert analysis.matched_event_id == "ai-agents-bootcamp", f"Failed to match Gen AI bootcamp for: {q}"


def test_normalize_event_category_typos():
    assert query_analyzer.analyze("hackaton").category_filter == "Hackathon"
    assert query_analyzer.analyze("hackathn").category_filter == "Hackathon"
    assert query_analyzer.analyze("workshp").category_filter == "Workshop"
    assert query_analyzer.analyze("iot worshop").category_filter == "Workshop"


def test_fuzzy_event_title_matching():
    # 'hackvers' should fuzzy-match 'HackVerse 2026'
    res1 = query_analyzer.analyze("hackvers")
    assert res1.matched_event_id == "hackverse-2026"

    # 'whr is hackverse'
    res2 = query_analyzer.analyze("whr is hackverse")
    assert res2.matched_event_id == "hackverse-2026"

    # 'iot embedded systems'
    res3 = query_analyzer.analyze("iot embedded systems")
    assert res3.matched_event_id == "iot-robotics-workshop"


def test_typo_relative_dates():
    res1 = query_analyzer.analyze("evnts tomorow")
    assert res1.date_label == "tomorrow"

    res2 = query_analyzer.analyze("events todai")
    assert res2.date_label == "today"

    res3 = query_analyzer.analyze("upcomming events")
    assert res3.wants_multiple is True
