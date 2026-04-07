"""
Localization Router - Currency formatting and fiscal year utilities
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
from services.localization_service import (
    CurrencyFormatter,
    FiscalYearHelper,
    format_inr,
    format_usd,
    format_dual_currency
)
from datetime import datetime

router = APIRouter()


class FormatCurrencyRequest(BaseModel):
    amount: float
    currency: Literal["INR", "USD", "EUR", "GBP", "AUTO"] = "AUTO"
    use_indian_format: bool = True
    decimals: int = 2


class FormatDualCurrencyRequest(BaseModel):
    amount: float
    primary_currency: Literal["INR", "USD", "EUR", "GBP"] = "INR"
    secondary_currency: Literal["INR", "USD", "EUR", "GBP"] = "USD"
    exchange_rate: float = 83.0
    decimals: int = 2


class FiscalYearRequest(BaseModel):
    date: str  # ISO format


@router.post("/format-currency")
async def format_currency(request: FormatCurrencyRequest):
    """
    Format amount as currency
    
    Examples:
        - 150000 INR → "₹1.5L"
        - 15000000 INR → "₹1.5Cr"
        - 1500000 USD → "$1.5M"
    """
    try:
        formatted = CurrencyFormatter.format(
            request.amount,
            request.currency,
            request.use_indian_format,
            request.decimals
        )
        
        return {
            "amount": request.amount,
            "formatted": formatted,
            "currency": request.currency
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/format-dual-currency")
async def format_dual_currency_endpoint(request: FormatDualCurrencyRequest):
    """
    Format with both currencies
    
    Example:
        - 15000000 INR → "₹1.5Cr ($180.72K)"
    """
    try:
        formatted = CurrencyFormatter.format_with_both(
            request.amount,
            request.primary_currency,
            request.secondary_currency,
            request.exchange_rate,
            request.decimals
        )
        
        return {
            "amount": request.amount,
            "formatted": formatted,
            "primary_currency": request.primary_currency,
            "secondary_currency": request.secondary_currency,
            "exchange_rate": request.exchange_rate
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/indian-fiscal-year")
async def get_indian_fiscal_year(request: FiscalYearRequest):
    """
    Get Indian fiscal year for a date
    
    Returns:
        - "FY2024-25" format
    """
    try:
        date = datetime.fromisoformat(request.date)
        fy = FiscalYearHelper.get_indian_fy(date)
        quarter = FiscalYearHelper.get_fy_quarters(date)
        
        return {
            "date": request.date,
            "fiscal_year": fy,
            "quarter": quarter
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/currency-symbols")
async def get_currency_symbols():
    """Get all supported currency symbols"""
    return {
        "symbols": CurrencyFormatter.SYMBOLS,
        "supported_currencies": list(CurrencyFormatter.SYMBOLS.keys())
    }


@router.get("/exchange-rates")
async def get_exchange_rates():
    """Get current exchange rates (mock - in production, fetch from API)"""
    return {
        "base": "INR",
        "rates": {
            "USD": 0.012,  # 1 INR = 0.012 USD
            "EUR": 0.011,
            "GBP": 0.0095
        },
        "inverse_rates": {
            "USD": 83.0,   # 1 USD = 83 INR
            "EUR": 90.0,
            "GBP": 105.0
        },
        "last_updated": datetime.now().isoformat()
    }
