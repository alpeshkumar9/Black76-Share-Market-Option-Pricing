import logging
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from rich import print
from typing import Union
from unittest.mock import patch
from sqlalchemy.orm import Session

from app.main import app
from app.database import Base, engine, Market
from app.schema.market import MarketPostBody, MarketPostResponse
from app.routes.market import black76_pv


@pytest.fixture(scope="session")
def test_app():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield app
    Base.metadata.drop_all(bind=engine)


def test_add_market_data_endpoint(db: Session):
    with TestClient(app) as client:
        with patch("app.database.get_db") as mock_get_db:
            mock_get_db.return_value = db

            # Define a sample market data object
            market_data = {
                "option": "AAPL",
                "option_type": "call",
                "underlying_price": 130.0,
                "strike_price": 135.0,
                "time_to_expiry": 0.25,
                "risk_free_rate": 0.01,
                "implied_volatility": 0.2
            }

            # Make a POST request to the add endpoint
            response = client.post("/option/add", json=market_data)

            # Verify that the response has a 200 status code and a success message
            assert response.status_code == 200
            assert response.json()["success"] == True
            assert response.json()[
                "message"] == "Market data created successfully."


@pytest.mark.asyncio
async def test_market_list(async_client: AsyncClient):
    """
    Test to check if the /option/list endpoint returns a 200 status code
    """
    response = await async_client.get("/option/list")
    assert response.status_code == 200


def test_present_value_endpoint(db: Session):
    """
    Test to check if the /option/present_value endpoint returns the correct present values for each option in the database
    """
    with TestClient(app) as client:
        with patch("app.database.get_db") as mock_get_db:
            mock_get_db.return_value = db

            response = client.get("/option/present_value")
            assert response.status_code == 200
            assert len(response.json()["response"]) == db.query(Market).count()
            for market in db.query(Market).all():
                present_value = round(black76_pv(market.underlying_price, market.strike_price, market.time_to_expiry,
                                      market.risk_free_rate, market.implied_volatility, market.option_type), 5)
                assert {"option": market.option, "present_value": present_value} in response.json()[
                    "response"]
