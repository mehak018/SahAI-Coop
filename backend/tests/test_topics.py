def test_get_topics_categories(client):
    response = client.get("/api/topics")
    assert response.status_code == 200
    topics = response.json()
    assert isinstance(topics, list)
    assert len(topics) >= 6
    
    # Check essential topics from SIH requirement
    slugs = [t["slug"] for t in topics]
    assert "crop-insurance" in slugs
    assert "pacs-services" in slugs
    assert "grievance-assistance" in slugs
    assert "required-documents" in slugs
    assert "cooperative-society-rules" in slugs
    assert "government-schemes" in slugs


def test_get_sample_questions(client):
    response = client.get("/api/sample-questions?language=en")
    assert response.status_code == 200
    questions = response.json()
    assert isinstance(questions, list)
    assert len(questions) > 0
    assert any("crop insurance" in q["question"].lower() for q in questions)


def test_get_sample_questions_marathi(client):
    response = client.get("/api/sample-questions?language=mr")
    assert response.status_code == 200
    questions = response.json()
    assert isinstance(questions, list)
    assert len(questions) > 0
    assert any("पीक" in q["question"] for q in questions)


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
