from app.services.conversation import conversation_manager


def test_conversation_memory_bounds():
    conv_id = "test-session-1"
    conversation_manager.clear_conversation(conv_id)

    for i in range(10):
        conversation_manager.add_message(conv_id, "user" if i % 2 == 0 else "assistant", f"Message {i}")

    history = conversation_manager.get_history(conv_id)
    assert len(history) <= 6
    assert history[-1].content == "Message 9"


def test_pronoun_resolution():
    conv_id = "test-session-2"
    conversation_manager.clear_conversation(conv_id)

    conversation_manager.add_message(conv_id, "user", "Tell me about HackVerse.")
    conversation_manager.add_message(conv_id, "assistant", "HackVerse is a 24-hour national hackathon.")

    resolved = conversation_manager.resolve_query_context("Where is it?", conv_id)
    assert "HackVerse" in resolved
