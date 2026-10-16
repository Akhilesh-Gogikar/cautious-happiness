import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core import security
from app.intelligence.api import mirror
from app.mirror.models import AnalysisResult

ROUTES = [("get", "/mirror/competitors"), ("post", "/mirror/analyze/opec_watch")]


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("ALLOW_DEMO_AUTH", raising=False)

    async def fake_analyze(query, target_id):
        return AnalysisResult(target_id=target_id, sentiment_score=0.1, crowd_conviction=0.5,
                              summary=f"analysis of {query}", key_phrases=[])

    monkeypatch.setattr(mirror.mirror_service, "analyze_target", fake_analyze)
    app = FastAPI()
    app.include_router(mirror.router)
    return TestClient(app)


def _bearer(username="analyst"):
    return {"Authorization": f"Bearer {security.create_access_token({'sub': username})}"}


@pytest.mark.parametrize("method, path", ROUTES)
@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer not-a-jwt"}])
def test_mirror_routes_refuse_requests_without_a_valid_token(client, method, path, headers):
    assert getattr(client, method)(path, headers=headers).status_code == 401


@pytest.mark.parametrize("method, path", ROUTES)
def test_mirror_routes_serve_signed_in_users(client, method, path):
    assert getattr(client, method)(path, headers=_bearer()).status_code == 200


def test_every_mirror_route_requires_sign_in():
    # The requirement sits on the router, so a route added later is covered too.
    for route in mirror.router.routes:
        dependencies = [d.call for d in route.dependant.dependencies]
        assert any(getattr(d, "__name__", "") == "get_current_active_user" for d in dependencies), route.path
