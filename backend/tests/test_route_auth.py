"""Sign-in on the routes QA-012 found open: news feed, strategy generation,
the alpha scanner and the demo pipeline (the /mirror routes are in
test_mirror_auth.py)."""
import importlib
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core import security
from app.intelligence.api import news
from app.routers import demo, scanner
from app.strategy.models import StrategyCode

# app.strategy re-exports its router under the module's name, so import the module itself.
strategy = importlib.import_module("app.strategy.router")

ROUTES = [
    ("get", "/intelligence/news", {}),
    ("get", "/intelligence/status", {}),
    ("post", "/strategy/generate", {"json": {"prompt": "mean reversion on Brent"}}),
    ("get", "/api/v1/scanner/assets", {}),
    ("post", "/demo/analyze", {"json": {"scenario": "OPEC cuts output"}}),
    ("post", "/demo/ingest_news", {"params": {"title": "t", "content": "c"}}),
]


@pytest.fixture
def orchestrator_requests():
    return []


@pytest.fixture
def client(monkeypatch, orchestrator_requests):
    monkeypatch.delenv("ALLOW_DEMO_AUTH", raising=False)
    monkeypatch.setattr(news.feed_manager, "fetch_news", lambda: [])

    async def fake_strategy(request):
        return StrategyCode(name="s", code="pass", description="d", logic_summary="l")

    async def fake_prices():
        return scanner._generate_synthetic_prices()

    monkeypatch.setattr(strategy.strategy_factory, "generate_strategy", fake_strategy)
    monkeypatch.setattr(scanner, "get_asset_prices", fake_prices)

    async def run_demo_pipeline(scenario):
        return {"scenario": scenario}

    async def ingest_news(title, content, category):
        return None

    def fake_orchestrator():
        # Building the real one loads a ~2 GB embedder.
        orchestrator_requests.append(True)
        return SimpleNamespace(run_demo_pipeline=run_demo_pipeline, news_agent=SimpleNamespace(ingest_news=ingest_news))

    app = FastAPI()
    for module_router in (news.router, strategy.router, scanner.router):
        app.include_router(module_router)
    app.include_router(demo.router, prefix="/demo")
    app.dependency_overrides[demo.get_orchestrator] = fake_orchestrator
    return TestClient(app)


def _bearer(username="analyst"):
    return {"Authorization": f"Bearer {security.create_access_token({'sub': username})}"}


@pytest.mark.parametrize("method, path, kwargs", ROUTES)
@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer not-a-jwt"}])
def test_routes_refuse_requests_without_a_valid_token(client, method, path, kwargs, headers):
    assert getattr(client, method)(path, headers=headers, **kwargs).status_code == 401


@pytest.mark.parametrize("method, path, kwargs", ROUTES)
def test_routes_serve_signed_in_users(client, method, path, kwargs):
    assert getattr(client, method)(path, headers=_bearer(), **kwargs).status_code == 200


@pytest.mark.parametrize("path, kwargs", [("/demo/analyze", ROUTES[4][2]), ("/demo/ingest_news", ROUTES[5][2])])
def test_demo_refuses_anonymous_callers_before_building_the_orchestrator(client, orchestrator_requests, path, kwargs):
    assert client.post(path, **kwargs).status_code == 401
    assert orchestrator_requests == []


@pytest.mark.parametrize("module_router", [news.router, strategy.router, scanner.router, demo.router])
def test_every_route_on_these_routers_requires_sign_in(module_router):
    # The requirement sits on each router, so a route added later is covered too.
    for route in module_router.routes:
        dependencies = [d.call for d in route.dependant.dependencies]
        assert any(getattr(d, "__name__", "") == "get_current_active_user" for d in dependencies), route.path
