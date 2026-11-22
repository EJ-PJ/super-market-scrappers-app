import base64
import json

import requests

# HTTP handler whit GET and POST methods

# seconds to wait for a supermarket before giving up
DEFAULT_TIMEOUT = 15


class BaseClient:

    def __init__(self):
        self.session = requests.Session()

    def get(self, url, **kwargs):
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        response = self.session.get(url, **kwargs)

        response.raise_for_status()

        return response

    def post(self, url, **kwargs):
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        response = self.session.post(url, **kwargs)

        response.raise_for_status()

        return response


# --- Location (postal code -> store) ---

class InvalidPostalCode(Exception):
    """The supermarket doesn't recognize the postal code (VTEX error ORD006)."""


class NoStoreForPostalCode(Exception):
    """The postal code is valid but the supermarket has no store for that zone."""


def encode_vtex_segment(sales_channel: int, region_id: str, seller: str) -> str:
    # VTEX stores (Maxi Despensa, Paiz, Walmart, La Torre) pick the store from the
    # "vtex_segment" cookie: a base64 JSON with the region and the store (seller).
    # regionId alone changes prices, "facets" also hides products that store doesn't sell
    segment = {
        "campaigns": None,
        "channel": str(sales_channel),
        "priceTables": None,
        "regionId": region_id,
        "utm_campaign": None,
        "utm_source": None,
        "utmi_campaign": None,
        "currencyCode": "GTQ",
        "currencySymbol": "Q",
        "countryCode": "GTM",
        "cultureInfo": "es-GT",
        "channelPrivacy": "public",
        "facets": f"accesscontrollist={seller};",
    }
    return base64.b64encode(json.dumps(segment).encode("utf-8")).decode("utf-8")
