"""Order checkout.

The rules live in `src/shop/specs/checkout.md` - read it first.
Both functions below are stubs: their signature is final, the bodies are yours.
Do not change the constants: the tests rely on them.
"""

PROMO_CODES = {"WELCOME10": 10, "SUMMER15": 15, "VIP35": 35}
SUPPORTED_CITIES = ("msk", "spb")
MAX_DISCOUNT_PERCENT = 30
VAT_PERCENT = 20
SHIPPING_KOPEKS = 49_000
FREE_DELIVERY_FROM_KOPEKS = 500_000
TIER_DISCOUNTS = ((10, 5), (25, 10), (50, 15))
REQUIRED_LINE_KEYS = ("sku", "qty", "unit_price_kopecks")


def validate_order(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> str | None:
    """Return a human readable reason why the order is invalid, or None if it is fine."""
    if not lines:
        return "order must contain at least one line"

    seen_skus: set[str] = set()

    for order_line in lines:
        for key in REQUIRED_LINE_KEYS:
            if key not in order_line:
                return f"missing required key: {key}"

        sku = order_line["sku"]
        if not sku:
            return "sku must not be empty"

        if sku in seen_skus:
            return "duplicate sku"
        seen_skus.add(sku)

        try:
            qty = int(order_line["qty"])
        except ValueError:
            return "qty must be a whole number"

        if qty <= 0:
            return "qty must be greater than zero"

        try:
            unit_price = int(order_line["unit_price_kopecks"])
        except ValueError:
            return "unit price must be a whole number"

        if unit_price < 0:
            return "unit price cannot be negative"

    if promo_code and promo_code not in PROMO_CODES:
        return "unknown promo code"

    if shipping_city and shipping_city not in SUPPORTED_CITIES:
        return "unsupported shipping city"

    return None


def calculate_order_total(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> int | None:
    """Return the order total in kopecks, or None if the order is invalid."""
    ...