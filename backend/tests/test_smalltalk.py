from app.ai.smalltalk import check_smalltalk_and_respond


def test_pure_smalltalk_greetings():
    greetings = [
        "hello",
        "hi",
        "hey",
        "hii",
        "hiii",
        "hello there",
        "good morning",
        "good afternoon",
        "good evening",
        "thanks",
        "thank you",
        "thanks bro",
        "bye",
        "goodbye",
        "who are you",
        "what can you do",
        "help",
    ]
    for g in greetings:
        is_st, response = check_smalltalk_and_respond(g)
        assert is_st is True, f"Failed to identify small talk: {g}"
        assert response is not None and len(response) > 0


def test_mixed_queries_pass_through():
    mixed_queries = [
        "hello, what events are happening today?",
        "hey, any gen ai events this week?",
        "good morning, where is HackVerse?",
        "hi, what is the registration deadline?",
        "thanks! what is the venue for the workshop?",
    ]
    for mq in mixed_queries:
        is_st, response = check_smalltalk_and_respond(mq)
        assert is_st is False, f"Mixed query was incorrectly intercepted as small talk: {mq}"
        assert response is None
