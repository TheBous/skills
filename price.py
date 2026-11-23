MAX_DISCOUNT = 0.30


def discounted(price_cents: int, discount: float) -> int:
    """Price after the discount, which is capped at MAX_DISCOUNT."""
    return round(price_cents * (1 - min(discount, MAX_DISCOUNT)))
