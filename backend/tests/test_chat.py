def test_create_and_get_chat_sessions(client):
    # Register user
    reg = client.post(
        "/api/auth/register",
        json={
            "name": "Chat User",
            "email": "chat.user@example.com",
            "password": "Password123",
            "preferred_language": "en"
        }
    )
    user_id = reg.json()["user"]["id"]

    # Create session
    create_res = client.post(
        "/api/chat/sessions",
        json={
            "user_id": user_id,
            "title": "PMFBY Clarifications"
        }
    )
    assert create_res.status_code == 201
    session_data = create_res.json()
    assert session_data["title"] == "PMFBY Clarifications"
    assert session_data["user_id"] == user_id
    session_id = session_data["id"]

    # Get user sessions
    list_res = client.get(f"/api/chat/sessions/{user_id}")
    assert list_res.status_code == 200
    sessions = list_res.json()
    assert len(sessions) >= 1
    assert any(s["id"] == session_id for s in sessions)


def test_send_message_matched_knowledge(client):
    # Register user and create session
    reg = client.post(
        "/api/auth/register",
        json={
            "name": "Farmer Ramesh",
            "email": "farmer.ramesh@example.com",
            "password": "Password123",
            "preferred_language": "en"
        }
    )
    user_id = reg.json()["user"]["id"]

    session_res = client.post(
        "/api/chat/sessions",
        json={"user_id": user_id, "title": "New Conversation"}
    )
    session_id = session_res.json()["id"]

    # Send message that matches crop insurance
    msg_res = client.post(
        "/api/chat/message",
        json={
            "session_id": session_id,
            "content": "How do I apply for crop insurance?",
            "language": "en"
        }
    )
    assert msg_res.status_code == 201
    data = msg_res.json()

    # Verify user message
    assert data["user_message"]["content"] == "How do I apply for crop insurance?"
    assert data["user_message"]["sender"] == "user"

    # Verify bot message and topic matching
    assert data["bot_message"]["sender"] == "bot"
    assert "PMFBY" in data["bot_message"]["content"]
    assert data["bot_message"]["topic_category"] == "Crop Insurance"
    assert "https://pmfby.gov.in" in data["bot_message"]["source_reference"]


def test_send_message_unmatched_fallback(client):
    reg = client.post(
        "/api/auth/register",
        json={
            "name": "Fallback User",
            "email": "fallback.user@example.com",
            "password": "Password123",
            "preferred_language": "en"
        }
    )
    user_id = reg.json()["user"]["id"]

    session_res = client.post(
        "/api/chat/sessions",
        json={"user_id": user_id}
    )
    session_id = session_res.json()["id"]

    # Send completely unrelated or unknown question
    msg_res = client.post(
        "/api/chat/message",
        json={
            "session_id": session_id,
            "content": "What is the quantum mechanics theory of photosynthesis?",
            "language": "en"
        }
    )
    assert msg_res.status_code == 201
    data = msg_res.json()
    assert data["bot_message"]["sender"] == "bot"
    assert data["bot_message"]["topic_category"] == "General Inquiry"
    assert "Ministry of Cooperation" in data["bot_message"]["source_reference"]


def test_get_chat_history(client):
    reg = client.post(
        "/api/auth/register",
        json={
            "name": "History User",
            "email": "history.user@example.com",
            "password": "Password123",
            "preferred_language": "en"
        }
    )
    user_id = reg.json()["user"]["id"]

    session_res = client.post(
        "/api/chat/sessions",
        json={"user_id": user_id, "title": "History Session"}
    )
    session_id = session_res.json()["id"]

    # Post message
    client.post(
        "/api/chat/message",
        json={
            "session_id": session_id,
            "content": "What is PACS?",
            "language": "en"
        }
    )

    # Fetch history
    history_res = client.get(f"/api/chat/history/{session_id}")
    assert history_res.status_code == 200
    data = history_res.json()
    assert data["session_id"] == session_id
    # Should have 2 messages (1 user, 1 bot)
    assert len(data["messages"]) == 2
    assert data["messages"][0]["sender"] == "user"
    assert data["messages"][1]["sender"] == "bot"
