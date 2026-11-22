import logging
from concurrent.futures import ThreadPoolExecutor

import requests

from app.clients.base_client import InvalidPostalCode, NoStoreForPostalCode
from app.scrapper.la_torre_scrapper import LaTorreScrapper
from app.scrapper.maxi_despensa_scrapper import MaxiDespensaScrapper
from app.scrapper.paiz_scrapper import PaizScrapper
from app.scrapper.super_fresh_scrapper import SuperFreshScrapper
from app.scrapper.walmart_scrapper import WalmartScrapper

logger = logging.getLogger(__name__)

# Every supported supermarket. To add a new one, create its scrapper
# (search_products(query, page, page_size, postal_code) -> list of make_product dicts)
# and register it here.
STORES = {
    "maxi_despensa": {"name": "Maxi Despensa", "scrapper": MaxiDespensaScrapper},
    "super_fresh": {"name": "Super Fresh", "scrapper": SuperFreshScrapper},
    "paiz": {"name": "Paiz", "scrapper": PaizScrapper},
    "walmart": {"name": "Walmart", "scrapper": WalmartScrapper},
    "la_torre": {"name": "La Torre", "scrapper": LaTorreScrapper},
}


class Products:

    # postal_code is optional: with it, each store returns the prices / products
    # of the store that delivers to that zone
    def search_products(self, query: str, store_ids: list[str], page: int, page_size: int,
                        postal_code: str | None = None) -> dict:
        # search every store at the same time, a slow or broken store
        # doesn't block or break the others
        with ThreadPoolExecutor(max_workers=len(store_ids)) as executor:
            results = list(executor.map(
                lambda store_id: self._search_store(store_id, query, page, page_size, postal_code),
                store_ids,
            ))

        return {
            "query": query,
            "page": page,
            "page_size": page_size,
            "postal_code": postal_code,
            "stores": [status for status, _ in results],
            "products": [product for _, products in results for product in products],
        }

    def _search_store(self, store_id: str, query: str, page: int, page_size: int, postal_code: str | None):
        store = STORES[store_id]
        status = {"id": store_id, "name": store["name"], "ok": True, "count": 0, "error": None}

        try:
            products = store["scrapper"]().search_products(query, page, page_size, postal_code)
        except (InvalidPostalCode, NoStoreForPostalCode) as error:
            status["ok"] = False
            status["error"] = error_message(error)
            return status, []
        except Exception as error:
            logger.exception("Error searching %s", store_id)
            status["ok"] = False
            status["error"] = error_message(error)
            return status, []

        status["count"] = len(products)
        return status, products


def error_message(error: Exception) -> str:
    if isinstance(error, InvalidPostalCode):
        return "La tienda no reconoce el código postal"
    if isinstance(error, NoStoreForPostalCode):
        return "La tienda no tiene sucursal para ese código postal"
    if isinstance(error, requests.HTTPError) and error.response is not None:
        return f"La tienda no respondió ({error.response.status_code})"
    if isinstance(error, requests.Timeout):
        return "La tienda tardó demasiado en responder"
    if isinstance(error, requests.ConnectionError):
        return "No se pudo conectar con la tienda"
    return "No se pudo leer la respuesta de la tienda"
