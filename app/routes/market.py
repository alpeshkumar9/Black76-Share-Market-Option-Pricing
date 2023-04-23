
from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.config import get_settings, get_logger
from app.schema.market import MarketPostBody, MarketPostResponse

from app.database import get_db, Market
import math
import scipy.stats as si

logger = get_logger()

router = APIRouter(prefix='/option', tags=["market"])

# API route to create a new market data entry


@router.post("/add",
             summary="Insert Market Data",
             description="To add new market option data",
             responses={
                 200: {"success": "Successful Response", "content": {"application/json": {"example": [{"success": True, "message": "Market data created successfully."}]}}}
             })
async def add(body: MarketPostBody, db: Session = Depends(get_db)):
    """
    Creates a new market data entry in the database.

    Parameters:
    - body: MarketPostBody object, containing the data to be added
    - db: SQLAlchemy Session object, for database interaction

    Returns:
    - dict: dictionary containing a success flag and a message indicating the result of the operation
    """
    try:
        # Create a new MarketData object from the input data
        new_market_data = Market(**body.dict())

        # Add the new market data to the database session
        db.add(new_market_data)

        # Commit the transaction to the database
        db.commit()

        # Return a success message
        return {"success": True, "message": "Market data created successfully."}

    except Exception as exception:
        return {"success": False, "message": "Failed to create market data: " + str(exception)}


@router.get('/list',
            summary="Market Data",
            description="Fetch Market Data",
            responses={
                200: {"description": "Successful Response", "content": {"application/json": {"example": [{"option": "AAPL", "option_type": "call", "present_value": 10.2}, {"option": "GOOG", "option_type": "put", "present_value": 12.5}]}}}
            })
async def options(db: Session = Depends(get_db)):

    """
    Fetches all market data entries from the database.

    Parameters:
    - db: SQLAlchemy Session object, for database interaction

    Returns:
    - dict: dictionary containing a list of all market data entries
    """
    market_data = db.query(Market).all()

    market_response = [MarketPostResponse(
        option=market.option,
        option_type=market.option_type,
        underlying_price=market.underlying_price,
        strike_price=market.strike_price,
        time_to_expiry=market.time_to_expiry,
        risk_free_rate=market.risk_free_rate,
        implied_volatility=market.implied_volatility,
    ) for market in market_data]

    logger.info('List fetched successfully')
    return {"data": market_response}


@router.get('/present_value',
            summary="Calculate PV",
            description="To find the PV value of the options",
            responses={
                200: {"description": "Successful Response", "content": {"application/json": {"example": [{"option": "AAPL", "option_type": "call", "present_value": 10.2}, {"option": "GOOG", "option_type": "put", "present_value": 12.5}]}}}
            })
async def present_value(db: Session = Depends(get_db)):

    """
    Calculates the present value of all options in the market data.

    Parameters:
    - db: SQLAlchemy Session object, for database interaction

    Returns:
    - dict: dictionary containing a list of present values for all options in the market data
    """
    market_data = db.query(Market).all()
    market_response = []
    for market in market_data:
        F = market.underlying_price
        K = market.strike_price
        T = market.time_to_expiry
        r = market.risk_free_rate
        sigma = market.implied_volatility
        pv = black76_pv(F, K, T, r, sigma, market.option_type)
        market_response.append({
            "option": market.option,
            "present_value": round(pv, 5),
        })
    return {"response": market_response}


def black76_pv(F, K, T, r, sigma, optionType):
    """
    Calculates the present value of a given option, based on the Black-76 model.

    PV = present value of the option
    r = risk-free interest rate
    T = time to expiration of the option (in years)
    F = current market price of the underlying futures contract
    K = strike price of the option
    N() = cumulative normal distribution function
    d1 = [ln(F/K) + (sigma^2/2) * T] / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    """
    d1 = (math.log(F/K) + 0.5 * sigma**2 * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if optionType == 'call':
        pv = math.exp(-r * T) * (F * norm_cdf(d1) - K * norm_cdf(d2))
    elif optionType == 'put':
        pv = math.exp(-r * T) * (K * norm_cdf(-d2) - F * norm_cdf(-d1))

    return pv


def norm_cdf(x):
    """
    Calculates the cumulative distribution function of the standard normal distribution
    """
    normsdist = si.norm.cdf(x, 0.0, 1.0)
    return (normsdist)
    # return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0
