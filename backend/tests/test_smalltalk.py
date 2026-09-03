from app.ai.smalltalk import check_smalltalk_and_respond


def test_pure_smalltalk_greetings():
    greetings = [
        "hello",
        "hi",
        "hey",
        "hii",
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
        "hello, what events are happening at Equinox?",
        "hey, tell me about IPL Auction",
        "good morning, where is MLRIT?",
        "hi, who can I contact?",
        "thanks! which event is like Monopoly?",
    ]
    for mq in mixed_queries:
        is_st, response = check_smalltalk_and_respond(mq)
        assert is_st is False, f"Mixed query was incorrectly intercepted as small talk: {mq}"
        assert response is None
