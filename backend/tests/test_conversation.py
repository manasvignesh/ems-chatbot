from app.services.conversation import ConversationManager


def test_conversation_sliding_window():
    cm = ConversationManager(max_history=4)
    conv_id = "test-conv-1"

    for i in range(6):
        cm.add_message(conv_id, "user", f"Msg {i}")

    history = cm.get_history(conv_id)
    assert len(history) == 4
    assert history[0].content == "Msg 2"
    assert history[-1].content == "Msg 5"


def test_pronoun_resolution_equinox():
    cm = ConversationManager()
    conv_id = "test-conv-2"

    cm.add_message(conv_id, "user", "Tell me about Startup Poly")
    cm.add_message(conv_id, "assistant", "Startup Poly is a business simulation inspired by Monopoly.")

    # User uses pronoun 'it'
    resolved = cm.resolve_query_context("How do I participate in it?", conv_id)
    assert "Startup Poly" in resolved or "startup poly" in resolved.lower()
