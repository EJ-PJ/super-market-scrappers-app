import base64
import json

import requests

from .base_client import BaseClient, InvalidPostalCode, NoStoreForPostalCode, encode_vtex_segment
from app.postal_code import get_postal_code_coords


class LaTorreClient:

    host = "https://www.latorre.com.gt"
    base_url = f"{host}/_v/segment/graphql/v1"
    # postal code -> region and store (seller)
    regions_url = f"{host}/api/checkout/pub/regions"
    # pickup points near some coordinates, they have the store address
    pickup_points_url = f"{host}/api/checkout/pub/pickup-points"

    # VTEX sales channel of La Torre ("sc" param)
    sales_channel = 1
    # La Torre returns one seller per zone (e.g. latorremxlatorrezona2).
    # Note: tested in Nov 2026, La Torre has the same prices in every store
    seller_prefix = "latorre"

    # postal code -> {"region_id", "seller"}, shared between requests
    _region_cache: dict = {}
    # postal code -> {"name", "address", "distance_km"}
    _branch_cache: dict = {}

    querystring = {"workspace": "master", "maxAge": "short", "appsEtag": "remove",
                   "domain": "store", "locale": "es-GT", "operationName": "productSearchV3",
                   "variables": "{}"}

    # persisted GraphQL query that VTEX expects inside "extensions"
    persisted_query = {"version": 1, "sha256Hash": "a96c5ed03ef513568c34b63a4bf8da055ea6296293ee02eadb56e2e895eaffbc",
                       "sender": "vtex.store-resources@0.x", "provider": "vtex.search-graphql@0.x"}

    # search variables (taken from the La Torre curl), sent base64 encoded in extensions["variables"]
    search_variables = {
        "skusFilter": "FIRST_AVAILABLE",
        "simulationBehavior": "default",
        "installmentCriteria": "MAX_WITHOUT_INTEREST",
        "productOriginVtex": False,
        "map": "ft",
        "query": "",
        "orderBy": "OrderByScoreDESC",
        "from": 0,
        "to": 19,
        "selectedFacets": [{"key": "ft", "value": ""}],
        "fullText": "",
        "operator": "and",
        "fuzzy": "0",
        "searchState": None,
        "hideUnavailableItems": True,
        "facetsBehavior": "Static",
        "categoryTreeBehavior": "default",
        "withFacets": False,
    }

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "content-type": "application/json",
        "Referer": "https://www.latorre.com.gt/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:153.0) Gecko/20100101 Firefox/153.0"
    }

    def search_products(self, product, from_index, to_index, postal_code=None):
        # copy so the class-level variables are never mutated between requests
        variables = {
            **self.search_variables,
            "query": product,
            "fullText": product,
            "selectedFacets": [{"key": "ft", "value": product}],
            "from": from_index,
            "to": to_index,
        }
        encoded_variables = base64.b64encode(json.dumps(variables).encode("utf-8")).decode("utf-8")

        querystring = dict(self.querystring)
        querystring["extensions"] = json.dumps({
            "persistedQuery": self.persisted_query,
            "variables": encoded_variables
        })

        # without postal code La Torre returns its default prices
        cookies = {}
        if postal_code:
            region = self.get_region(postal_code)
            cookies["vtex_segment"] = encode_vtex_segment(self.sales_channel, region["region_id"], region["seller"])

        response = BaseClient().get(
            self.base_url,
            headers=self.headers,
            params=querystring,
            cookies=cookies,
        )

        return response.json()

    def get_region(self, postal_code):
        if postal_code in self._region_cache:
            return self._region_cache[postal_code]

        try:
            response = BaseClient().get(
                self.regions_url,
                headers=self.headers,
                params={"country": "GTM", "sc": self.sales_channel, "postalCode": postal_code},
            )
        except requests.HTTPError as error:
            # 400 = ORD006 "codigo postal no válido"
            if error.response is not None and error.response.status_code == 400:
                raise InvalidPostalCode(postal_code) from error
            raise

        regions = response.json()
        sellers = {seller["id"]: seller.get("name") for seller in (regions[0].get("sellers") or [])} if regions else {}
        if not sellers:
            raise NoStoreForPostalCode(postal_code)

        # only the store's own branches: other sellers are marketplace vendors
        # (e.g. Walmart in Huehuetenango only has "Andreiso store")
        seller = next((s for s in sellers if s.startswith(self.seller_prefix)), None)
        if seller is None:
            raise NoStoreForPostalCode(postal_code)
        region = {"region_id": regions[0]["id"], "seller": seller, "seller_name": sellers[seller] or seller}

        self._region_cache[postal_code] = region
        return region

    def get_branch(self, postal_code):
        # store (branch) used for this postal code: name, address and distance to the zone.
        # None without postal code (the store uses its default prices)
        if not postal_code:
            return None
        if postal_code in self._branch_cache:
            return self._branch_cache[postal_code]

        region = self.get_region(postal_code)
        branch = {"name": self.branch_name(region), "address": None, "distance_km": None}

        # the pickup points near the zone have the address, their id starts with the seller
        coords = get_postal_code_coords(postal_code)
        if coords:
            response = BaseClient().get(
                self.pickup_points_url,
                headers=self.headers,
                params={"geoCoordinates": f"{coords['longitude']};{coords['latitude']}", "sc": self.sales_channel},
            )
            for item in response.json().get("items") or []:
                point = item.get("pickupPoint") or {}
                if not str(point.get("id", "")).startswith(region["seller"] + "_"):
                    continue
                address = point.get("address") or {}
                branch["name"] = point.get("friendlyName") or branch["name"]
                branch["address"] = ", ".join(p for p in (address.get("street"), address.get("city")) if p) or None
                if item.get("distance") is not None:
                    branch["distance_km"] = round(item["distance"], 1)
                break

        self._branch_cache[postal_code] = branch
        return branch

    def branch_name(self, region):
        # La Torre only sends ids as names ("latorremxlatorre20calle") and its pickup
        # points don't match the sellers, so the address is not available
        name = region["seller"].removeprefix("latorremx").removeprefix("latorre")
        return f"La Torre {name}" if name else "La Torre"
