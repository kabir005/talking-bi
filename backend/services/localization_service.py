"""
Localization Service - Multi-currency formatting with Indian and US standards
Supports: INR (Rs/L/Cr), USD ($), EUR (€), GBP (£)
"""

from typing import Union, Literal
from decimal import Decimal
import re

CurrencyType = Literal["INR", "USD", "EUR", "GBP", "AUTO"]


class CurrencyFormatter:
    """Format numbers as currency with locale-specific rules"""
    
    # Currency symbols
    SYMBOLS = {
        "INR": "₹",
        "USD": "$",
        "EUR": "€",
        "GBP": "£"
    }
    
    # Indian number system thresholds
    LAKH = 100_000
    CRORE = 10_000_000
    
    @classmethod
    def format(
        cls,
        amount: Union[int, float, Decimal],
        currency: CurrencyType = "AUTO",
        use_indian_format: bool = True,
        decimals: int = 2
    ) -> str:
        """
        Format amount as currency
        
        Args:
            amount: Number to format
            currency: Currency code (INR, USD, EUR, GBP, AUTO)
            use_indian_format: Use Indian numbering (L/Cr) for INR
            decimals: Decimal places
        
        Returns:
            Formatted string (e.g., "₹1.5Cr", "$1.5M")
        
        Examples:
            >>> format(150000, "INR", True)
            "₹1.5L"
            >>> format(15000000, "INR", True)
            "₹1.5Cr"
            >>> format(1500000, "USD", False)
            "$1.5M"
        """
        if amount is None or (isinstance(amount, float) and amount != amount):  # NaN check
            return "N/A"
        
        amount = float(amount)
        
        # Auto-detect currency (default to INR for Indian context)
        if currency == "AUTO":
            currency = "INR"
        
        symbol = cls.SYMBOLS.get(currency, "")
        
        # Indian format (Lakh/Crore)
        if currency == "INR" and use_indian_format:
            return cls._format_indian(amount, symbol, decimals)
        
        # Western format (K/M/B)
        return cls._format_western(amount, symbol, decimals)
    
    @classmethod
    def _format_indian(cls, amount: float, symbol: str, decimals: int) -> str:
        """Format using Indian numbering system (Lakh/Crore)"""
        abs_amount = abs(amount)
        sign = "-" if amount < 0 else ""
        
        if abs_amount >= cls.CRORE:
            # Crores
            value = abs_amount / cls.CRORE
            suffix = "Cr"
        elif abs_amount >= cls.LAKH:
            # Lakhs
            value = abs_amount / cls.LAKH
            suffix = "L"
        elif abs_amount >= 1000:
            # Thousands
            value = abs_amount / 1000
            suffix = "K"
        else:
            # Less than 1000
            return f"{sign}{symbol}{abs_amount:,.{decimals}f}"
        
        # Format with appropriate decimals
        formatted_value = f"{value:.{decimals}f}".rstrip('0').rstrip('.')
        return f"{sign}{symbol}{formatted_value}{suffix}"
    
    @classmethod
    def _format_western(cls, amount: float, symbol: str, decimals: int) -> str:
        """Format using Western numbering system (K/M/B)"""
        abs_amount = abs(amount)
        sign = "-" if amount < 0 else ""
        
        if abs_amount >= 1_000_000_000:
            # Billions
            value = abs_amount / 1_000_000_000
            suffix = "B"
        elif abs_amount >= 1_000_000:
            # Millions
            value = abs_amount / 1_000_000
            suffix = "M"
        elif abs_amount >= 1_000:
            # Thousands
            value = abs_amount / 1_000
            suffix = "K"
        else:
            # Less than 1000
            return f"{sign}{symbol}{abs_amount:,.{decimals}f}"
        
        # Format with appropriate decimals
        formatted_value = f"{value:.{decimals}f}".rstrip('0').rstrip('.')
        return f"{sign}{symbol}{formatted_value}{suffix}"
    
    @classmethod
    def format_with_both(
        cls,
        amount: Union[int, float, Decimal],
        primary_currency: CurrencyType = "INR",
        secondary_currency: CurrencyType = "USD",
        exchange_rate: float = 83.0,  # INR to USD rate
        decimals: int = 2
    ) -> str:
        """
        Format with both currencies
        
        Args:
            amount: Amount in primary currency
            primary_currency: Primary currency code
            secondary_currency: Secondary currency code
            exchange_rate: Conversion rate (primary to secondary)
            decimals: Decimal places
        
        Returns:
            "₹1.5Cr ($180K)" or "$1.5M (₹12.45Cr)"
        
        Examples:
            >>> format_with_both(15000000, "INR", "USD", 83.0)
            "₹1.5Cr ($180.72K)"
        """
        if amount is None or (isinstance(amount, float) and amount != amount):
            return "N/A"
        
        # Format primary
        primary_formatted = cls.format(
            amount,
            primary_currency,
            use_indian_format=(primary_currency == "INR"),
            decimals=decimals
        )
        
        # Convert and format secondary
        if primary_currency == "INR" and secondary_currency == "USD":
            secondary_amount = amount / exchange_rate
        elif primary_currency == "USD" and secondary_currency == "INR":
            secondary_amount = amount * exchange_rate
        else:
            # For other conversions, use provided rate
            secondary_amount = amount / exchange_rate
        
        secondary_formatted = cls.format(
            secondary_amount,
            secondary_currency,
            use_indian_format=(secondary_currency == "INR"),
            decimals=decimals
        )
        
        return f"{primary_formatted} ({secondary_formatted})"
    
    @classmethod
    def parse_indian_number(cls, text: str) -> float:
        """
        Parse Indian formatted number back to float
        
        Examples:
            >>> parse_indian_number("₹1.5Cr")
            15000000.0
            >>> parse_indian_number("₹2.5L")
            250000.0
        """
        # Remove currency symbols
        text = re.sub(r'[₹$€£,]', '', text).strip()
        
        # Extract number and suffix
        match = re.match(r'([-+]?\d+\.?\d*)\s*([KLCrMB])?', text, re.IGNORECASE)
        if not match:
            raise ValueError(f"Cannot parse: {text}")
        
        number = float(match.group(1))
        suffix = match.group(2)
        
        if suffix:
            suffix = suffix.upper()
            multipliers = {
                'K': 1_000,
                'L': 100_000,
                'CR': 10_000_000,
                'M': 1_000_000,
                'B': 1_000_000_000
            }
            number *= multipliers.get(suffix, 1)
        
        return number


class FiscalYearHelper:
    """Helper for Indian Fiscal Year (April-March)"""
    
    @staticmethod
    def get_indian_fy(date) -> str:
        """
        Get Indian FY for a date
        
        Args:
            date: datetime object or string
        
        Returns:
            "FY2024-25" format
        
        Examples:
            >>> get_indian_fy(datetime(2024, 5, 15))
            "FY2024-25"
            >>> get_indian_fy(datetime(2024, 2, 15))
            "FY2023-24"
        """
        from datetime import datetime
        
        if isinstance(date, str):
            date = datetime.fromisoformat(date)
        
        year = date.year
        month = date.month
        
        # Indian FY starts in April
        if month >= 4:
            fy_start = year
            fy_end = year + 1
        else:
            fy_start = year - 1
            fy_end = year
        
        return f"FY{fy_start}-{str(fy_end)[-2:]}"
    
    @staticmethod
    def get_fy_quarters(date) -> str:
        """
        Get Indian FY quarter
        
        Returns:
            "Q1 FY2024-25" format
        
        Quarters:
            Q1: Apr-Jun
            Q2: Jul-Sep
            Q3: Oct-Dec
            Q4: Jan-Mar
        """
        from datetime import datetime
        
        if isinstance(date, str):
            date = datetime.fromisoformat(date)
        
        month = date.month
        
        # Determine quarter
        if 4 <= month <= 6:
            quarter = "Q1"
        elif 7 <= month <= 9:
            quarter = "Q2"
        elif 10 <= month <= 12:
            quarter = "Q3"
        else:  # 1-3
            quarter = "Q4"
        
        fy = FiscalYearHelper.get_indian_fy(date)
        return f"{quarter} {fy}"


# Convenience functions
def format_inr(amount: Union[int, float], decimals: int = 2) -> str:
    """Quick format as INR with L/Cr"""
    return CurrencyFormatter.format(amount, "INR", True, decimals)


def format_usd(amount: Union[int, float], decimals: int = 2) -> str:
    """Quick format as USD with K/M/B"""
    return CurrencyFormatter.format(amount, "USD", False, decimals)


def format_dual_currency(
    amount: Union[int, float],
    primary: CurrencyType = "INR",
    rate: float = 83.0,
    decimals: int = 2
) -> str:
    """Quick format with both INR and USD"""
    secondary = "USD" if primary == "INR" else "INR"
    return CurrencyFormatter.format_with_both(
        amount, primary, secondary, rate, decimals
    )
