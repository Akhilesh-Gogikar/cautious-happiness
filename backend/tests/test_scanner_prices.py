import asyncio

from app.routers import scanner


def test_get_asset_prices_uses_fallback_chain(monkeypatch):
    async def fake_yahoo(_client):
        return {"XOM": 101.5}

    async def fake_stooq(_client, stooq_symbol):
        if stooq_symbol == "cvx.us":
            return 202.25
        return None

    def fake_synthetic():
        return {asset["symbol"]: 9.99 for asset in scanner.ASSET_CATALOG}

    monkeypatch.setattr(scanner, "_fetch_yahoo_prices", fake_yahoo)
    monkeypatch.setattr(scanner, "_fetch_stooq_price", fake_stooq)
    monkeypatch.setattr(scanner, "_generate_synthetic_prices", fake_synthetic)

    prices = asyncio.run(scanner.get_asset_prices())

    assert prices["XOM"] == 101.5
    assert prices["CVX"] == 202.25
    assert prices["BRENT"] == 9.99
    assert len(prices) == len(scanner.ASSET_CATALOG)


def test_get_asset_prices_handles_yahoo_failure(monkeypatch):
    async def fake_yahoo(_client):
        raise RuntimeError("yahoo down")

    async def fake_stooq(_client, _stooq_symbol):
        return None

    def fake_synthetic():
        return {asset["symbol"]: 7.77 for asset in scanner.ASSET_CATALOG}

    monkeypatch.setattr(scanner, "_fetch_yahoo_prices", fake_yahoo)
    monkeypatch.setattr(scanner, "_fetch_stooq_price", fake_stooq)
    monkeypatch.setattr(scanner, "_generate_synthetic_prices", fake_synthetic)

    prices = asyncio.run(scanner.get_asset_prices())

    assert all(price == 7.77 for price in prices.values())


def test_get_asset_prices_fetches_stooq_fallbacks_concurrently(monkeypatch):
    async def fake_yahoo(_client):
        return {}

    started = []
    released = []
    gate = asyncio.Event()

    async def fake_stooq(_client, stooq_symbol):
        started.append(stooq_symbol)
        await gate.wait()
        released.append(stooq_symbol)
        return None

    def fake_synthetic():
        return {asset["symbol"]: 5.55 for asset in scanner.ASSET_CATALOG}

    monkeypatch.setattr(scanner, "_fetch_yahoo_prices", fake_yahoo)
    monkeypatch.setattr(scanner, "_fetch_stooq_price", fake_stooq)
    monkeypatch.setattr(scanner, "_generate_synthetic_prices", fake_synthetic)

    async def run_check():
        task = asyncio.create_task(scanner.get_asset_prices())

        for _ in range(200):
            if len(started) == len(scanner.ASSET_CATALOG):
                break
            await asyncio.sleep(0)

        assert len(started) == len(scanner.ASSET_CATALOG)
        assert released == []

        gate.set()
        prices = await task

        assert all(price == 5.55 for price in prices.values())

    asyncio.run(run_check())
