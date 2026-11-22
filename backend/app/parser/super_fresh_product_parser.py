from app.models import make_product, safe_get

STORE = "super_fresh"


class SuperFreshScrapperProduct:

    def product_parser(self, products: dict) -> list[dict]:
        parsed = []

        for product in safe_get(products, "products", default=[]):
            # "offer" can come as null when the product has no discount
            offer_price = safe_get(product, "offer", "price")
            normal_price = product.get("price")

            bar_code = product.get("barcode")

            brand = product.get("brand")
            if isinstance(brand, dict):
                brand = brand.get("name")

            parsed.append(make_product(
                store=STORE,
                product_id=bar_code or product.get("id"),
                name=product.get("description"),
                brand=brand,
                price=offer_price if offer_price is not None else normal_price,
                regular_price=normal_price,
                image=safe_get(product, "images", 0, "url"),
                url=f"https://www.misuperfresh.com.gt/product/{bar_code}" if bar_code else None,
                # Super Fresh only has two levels: subcategory -> category
                category=safe_get(product, "subcategory", "category", "name"),
                subcategory=safe_get(product, "subcategory", "name"),
            ))

        return parsed
