from typing import Optional, Union
from pydantic import BaseModel, Field


class MarketPostResponse(BaseModel):
    option: str
    option_type: str
    underlying_price: Optional[float]
    strike_price: Optional[float]
    time_to_expiry: Optional[float]
    risk_free_rate: Optional[float]
    implied_volatility: Optional[float]


class MarketPostBody(BaseModel):
    option: str
    option_type: str
    underlying_price: Optional[float]
    strike_price: Optional[float]
    time_to_expiry: Optional[float]
    risk_free_rate: Optional[float]
    implied_volatility: Optional[float]
    