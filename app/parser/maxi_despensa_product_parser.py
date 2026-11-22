from app.models import make_product, safe_get
from app.parser.promo_parser_maxi_despensa import ParserPromo

STORE = "maxi_despensa"


class MaxiDespensaScrapperProduct:

    def product_parser(self, products: dict) -> list[dict]:
        parser_promo = ParserPromo()
        parsed = []

        for product in safe_get(products, "data", "productSearch", "products", default=[]):
            offer = safe_get(product, "items", 0, "sellers", 0, "commertialOffer", default={})
            department, category, subcategory = parse_category(safe_get(product, "categories", 0))

            # the direct discount is already in price / regular_price / discount_percent,
            # keep only the other promotions (2 x Q20, combos, badges)
            promotions = [p for p in parser_promo.extract_promos(product) if p.get("type") != "discount"]

            link = product.get("linkText")

            parsed.append(make_product(
                store=STORE,
                product_id=product.get("productId"),
                name=product.get("productName"),
                brand=product.get("brand"),
                # Price is the price with discount, ListPrice is the real price
                price=offer.get("Price"),
                regular_price=offer.get("ListPrice"),
                image=safe_get(product, "items", 0, "images", 0, "imageUrl"),
                url=f"https://www.maxidespensa.com.gt/{link}/p" if link else None,
                department=department,
                category=category,
                subcategory=subcategory,
                promotions=promotions,
            ))

        return parsed


def parse_category(category: str | None):
    # VTEX sends "/Lácteos/Leche/Leche Entera/" -> department, category, subcategory
    # some products have fewer levels, missing ones are None
    levels = [level for level in (category or "").split("/") if level]
    levels += [None] * (3 - len(levels))
    return levels[0], levels[1], levels[2]
