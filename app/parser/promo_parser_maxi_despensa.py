import re

# "Promo,10x2,2026-07-20-2026-10-06-..." -> solo se usa para sacar las fechas
TEASER_RE = re.compile(r"^(\w+),([\d.]+)x(\d+),(\d{4}-\d{2}-\d{2})-(\d{4}-\d{2}-\d{2})")

# clusterHighlights que la tienda muestra como etiqueta (buscar por id, no por texto)
BADGE_CLUSTERS = {
    "6269": "Precio bajo exclusivo en línea",
}


class ParserPromo:

    def extract_promos(self, product: dict):
        offer = self.get_offer(product)
        if offer is None:
            return []

        promos = []
        discount = self.extract_discount(offer)
        if discount:
            promos.append(discount)
        promos.extend(self.extract_teasers(offer))
        promos.extend(self.extract_badges(product))
        return promos

    def get_offer(self, product: dict):
        # commertialOffer del primer seller del primer SKU
        try:
            return product["items"][0]["sellers"][0]["commertialOffer"]
        except (KeyError, IndexError):
            return None

    def extract_discount(self, offer: dict):
        # rebaja directa: ListPrice > Price -> "-20%"
        list_price = offer.get("ListPrice") or 0
        price = offer.get("Price") or 0
        if list_price <= price or list_price <= 0:
            return None

        pct = round((1 - price / list_price) * 100)
        return {
            "type": "discount",
            "label": f"-{pct}%",
            "list_price": list_price,
            "price": price,
            "percent": pct,
        }


    def extract_teasers(self, offer: dict):
        # promos por cantidad: "2 x Q20", "Combina 3 x Q30"
        promos, seen = [], set()
        price = offer.get("Price") or 0

        for teaser in offer.get("teasers") or []:
            name = teaser.get("name", "")
            # a veces el teaser viene duplicado
            if name in seen:
                continue
            seen.add(name)

            effects = {e["name"]: e["value"] for e in teaser["effects"]["parameters"]}
            conds = {c["name"]: c["value"] for c in teaser["conditions"]["parameters"]}
            # formato desconocido
            if "MaximumUnitPriceDiscount" not in effects:
                continue

            # el precio viene en centavos
            unit_price = int(effects["MaximumUnitPriceDiscount"]) / 100
            qty = teaser["conditions"]["minimumQuantity"]
            sku_ids = [s for s in conds.get("SkuIdsList", "").split(",") if s]
            is_combo = len(sku_ids) > 1 or "TYPE_PROMO_CMF" in name
            match = TEASER_RE.match(name)

            promos.append({
                "type": "combo" if is_combo else "bundle",
                "label": f"{'Combina ' if is_combo else ''}{qty} x Q{unit_price * qty:g}",
                "unit_price": unit_price,
                "min_qty": qty,
                "total_price": round(unit_price * qty, 2),
                "savings_per_unit": round(price - unit_price, 2),
                "sku_ids": sku_ids,
                "valid_from": match.group(4) if match else None,
                "valid_to": match.group(5) if match else None,
            })
        return promos

    def extract_badges(self, product: dict):
        # etiquetas como "Precio bajo exclusivo en línea"
        return [
            {"type": "badge", "label": BADGE_CLUSTERS[c["id"]]}
            for c in product.get("clusterHighlights") or []
            if c.get("id") in BADGE_CLUSTERS
        ]
