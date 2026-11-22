# Common product format shared by every supermarket.
# Each parser must return a list of dicts built with make_product so the
# frontend always receives the same keys, no matter the store.


def make_product(
    *,
    store: str,
    product_id,
    name: str | None,
    price,
    regular_price=None,
    brand: str | None = None,
    image: str | None = None,
    url: str | None = None,
    department: str | None = None,
    category: str | None = None,
    subcategory: str | None = None,
    promotions: list | None = None,
    currency: str = "GTQ",
    available: bool = True,
) -> dict:
    price = to_number(price)
    # a price of 0 means the store has no stock / no price for it
    if not price:
        price = None
    # regular_price is the price without discount; if the store doesn't send it,
    # it's the same as the current price
    regular_price = to_number(regular_price) or None
    if regular_price is None or (price is not None and regular_price < price):
        regular_price = price

    discount_percent = 0
    if price is not None and regular_price and regular_price > price:
        discount_percent = round((1 - price / regular_price) * 100)

    return {
        "id": f"{store}:{product_id}",
        "store": store,
        "name": name,
        "brand": brand,
        # price: what you pay today (with discount if there is one)
        "price": price,
        # regular_price: price before discount
        "regular_price": regular_price,
        "discount_percent": discount_percent,
        "currency": currency,
        # False when out of stock or without price, don't use it to compare
        "available": bool(available and price is not None),
        "promotions": promotions or [],
        "image": image,
        "url": url,
        "category": {
            "department": department,
            "category": category,
            "subcategory": subcategory,
        },
    }


def to_number(value):
    if value is None or value == "":
        return None
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None


def safe_get(data, *keys, default=None):
    for key in keys:
        try:
            data = data[key]
        except (KeyError, IndexError, TypeError):
            return default
    return default if data is None else data
