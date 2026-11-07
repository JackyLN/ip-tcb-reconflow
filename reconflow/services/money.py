"""Integer minor-unit math; round fee half-up per payout, never per payment."""

from decimal import Decimal

EXPONENTS = {"VND": 0, "USD": 2}


def fee(gross: int, basis_points: int) -> int:
    if gross < 0 or not 0 <= basis_points <= 10000:
        raise ValueError("Invalid fee input")
    return (gross * basis_points + 5000) // 10000


def minor(value: str, currency: str) -> int:
    scale = 10 ** EXPONENTS[currency]
    amount = Decimal(value) * scale
    if not amount.is_finite() or amount != amount.to_integral_value():
        raise ValueError("Invalid currency precision")
    return int(amount)


def display(value: int, currency: str) -> str:
    exponent = EXPONENTS[currency]
    return f"{Decimal(value) / (10**exponent):,.{exponent}f} {currency}"


def net(gross: int, refunds: int, fees: int, adjustment: int = 0) -> int:
    if not 0 <= refunds <= gross or fees < 0:
        raise ValueError("Invalid financial components")
    return gross - refunds - fees + adjustment
