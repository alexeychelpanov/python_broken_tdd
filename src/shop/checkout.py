"""Order checkout.

The rules live in `src/shop/specs/checkout.md` - read it first.
Do not change the constants: the tests rely on them.
"""

import re
import sys

from shop.money import percent_of

PROMO_CODES = {"WELCOME10": 10, "SUMMER15": 15, "VIP35": 35}
SUPPORTED_CITIES = ("msk", "spb")
MAX_DISCOUNT_PERCENT = 30
VAT_PERCENT = 20
SHIPPING_KOPEKS = 49_000
FREE_DELIVERY_FROM_KOPEKS = 500_000
TIER_DISCOUNTS = ((10, 5), (25, 10), (50, 15))
REQUIRED_LINE_KEYS = ("sku", "qty", "unit_price_kopecks")


def _parse_integer(value: str) -> int | None:
    """Check the decimal syntax before conversion because exceptions are forbidden."""
    stripped = value.strip()
    if re.fullmatch(r"[+-]?\d(?:_?\d)*", stripped) is None:
        return None
    # Python rejects decimal strings beyond its configured conversion limit.
    limit = sys.get_int_max_str_digits()
    if limit and len(stripped.lstrip("+-").replace("_", "")) > limit:
        return None
    return int(stripped)


def _validate_line(line: dict[str, str], number: int) -> str | None:
    """Validate one warehouse row and identify its position in error messages."""
    for key in REQUIRED_LINE_KEYS:
        if key not in line:
            return f"Line {number}: missing {key}"
    if not line["sku"]:
        return f"Line {number}: SKU must not be empty"
    quantity = _parse_integer(line["qty"])
    if quantity is None or quantity <= 0:
        return f"Line {number}: quantity must be a positive integer"
    price = _parse_integer(line["unit_price_kopecks"])
    if price is None or price < 0:
        return f"Line {number}: price must be a non-negative integer"
    return None


def validate_order(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> str | None:
    """Return a human readable reason why the order is invalid, or None if it is fine."""
    if not lines:
        return "Order must contain at least one line"
    seen: list[str] = []
    for number, line in enumerate(lines, start=1):
        reason = _validate_line(line, number)
        if reason is not None:
            return reason
        if line["sku"] in seen:
            return f"Line {number}: duplicate SKU"
        seen.append(line["sku"])
    if promo_code and promo_code not in PROMO_CODES:
        return "Unknown promo code"
    if shipping_city and shipping_city not in SUPPORTED_CITIES:
        return "Unsupported shipping city"
    return None


def calculate_order_total(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> int | None:
    """Return the order total in kopecks, or None if the order is invalid."""
    if validate_order(lines, promo_code, shipping_city) is not None:
        return None
    subtotal = sum(int(line["qty"]) * int(line["unit_price_kopecks"]) for line in lines)
    quantity = sum(int(line["qty"]) for line in lines)
    tier_percent = max(
        (percent for threshold, percent in TIER_DISCOUNTS if quantity >= threshold),
        default=0,
    )
    discount_percent = min(max(tier_percent, PROMO_CODES.get(promo_code, 0)), MAX_DISCOUNT_PERCENT)
    discounted_subtotal = subtotal - percent_of(subtotal, discount_percent)
    shipping = (
        SHIPPING_KOPEKS if shipping_city and discounted_subtotal < FREE_DELIVERY_FROM_KOPEKS else 0
    )
    base = discounted_subtotal + shipping
    return base + percent_of(base, VAT_PERCENT)
