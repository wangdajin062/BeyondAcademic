from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health_and_root():
    health = client.get('/health')
    assert health.status_code == 200
    assert health.json()['status'] == 'healthy'

    root = client.get('/')
    assert root.status_code == 200
    data = root.json()
    assert data['name'] == 'BeyondAcademic'


def test_article_workflow_versioning():
    create_payload = {
        'title': 'Integration Test Article',
        'content': 'Introduction',
        'template': 'IEEE',
    }
    created = client.post('/api/articles/?author=tester', json=create_payload)
    assert created.status_code == 201
    article = created.json()
    article_id = article['article_id']
    assert article['current_version'] == 1

    updated = client.put(
        f'/api/articles/{article_id}?author=tester',
        json={'content': 'Introduction updated', 'changes_summary': 'Edited intro'},
    )
    assert updated.status_code == 200
    assert updated.json()['current_version'] == 2

    versions = client.get(f'/api/articles/{article_id}/versions')
    assert versions.status_code == 200
    assert len(versions.json()) == 2


def test_editor_grammar_detects_multiple_issues():
    resp = client.post(
        '/api/editor/check/grammar',
        json={'text': 'We dont agree. The results shows improvement.', 'template': 'IEEE'},
    )
    assert resp.status_code == 200
    suggestions = resp.json()
    assert any(s['suggestion'] == "don't" for s in suggestions)
    assert any(s['suggestion'] == 'results show' for s in suggestions)


def test_test_login_success_and_failure():
    ok = client.post('/api/auth/test-login', json={'username': 'tester', 'password': 'test123456'})
    assert ok.status_code == 200
    payload = ok.json()
    assert payload['token_type'] == 'bearer'
    assert payload['user']['username'] == 'tester'

    bad = client.post('/api/auth/test-login', json={'username': 'tester', 'password': 'wrongpass'})
    assert bad.status_code == 401
