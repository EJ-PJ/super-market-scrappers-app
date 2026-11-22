import json

import requests

from .base_client import BaseClient, InvalidPostalCode, NoStoreForPostalCode, encode_vtex_segment
from app.parser.maxi_despensa_search_product_parser import ParserMaxiDespensa


class MaxiDespensaClient:

    host = "https://www.maxidespensa.com.gt"
    base_url = f"{host}/_v/segment/graphql/v1"
    # postal code -> region and store (seller)
    regions_url = f"{host}/api/checkout/pub/regions"

    # VTEX sales channel of Maxi Despensa ("sc" param)
    sales_channel = 3
    # the regions endpoint also returns "walmartgtwm99995" (WM Interior Bodega),
    # the Maxi Despensa store is the one that starts with this
    seller_prefix = "walmartgtbo"

    # postal code -> {"region_id", "seller"}, shared between requests
    _region_cache: dict = {}

    querystring = {"workspace":"master","maxAge":"short","appsEtag":"remove",
                   "domain":"store","locale":"es-GT","operationName":"productSearchV3",
                   "variables":"{}"}

    # persisted GraphQL query that VTEX expects inside "extensions"
    persisted_query = {"version":1,"sha256Hash":"a96c5ed03ef513568c34b63a4bf8da055ea6296293ee02eadb56e2e895eaffbc",
                       "sender":"vtex.store-resources@0.x","provider":"vtex.search-graphql@0.x"}

    # search variables, sent base64 encoded in extensions["variables"]
    search_variables = "{\"skusFilter\":\"ALL\",\"simulationBehavior\":\"default\",\"installmentCriteria\":\"MAX_WITHOUT_INTEREST\",\"productOriginVtex\":false,\"map\":\"ft\",\"query\":\"monster\",\"orderBy\":\"OrderByScoreDESC\",\"from\":0,\"to\":20,\"selectedFacets\":[{\"key\":\"ft\",\"value\":\"monster\"}],\"fullText\":\"monster\",\"facetsBehavior\":\"Static\",\"categoryTreeBehavior\":\"default\",\"withFacets\":false,\"variant\":\"6aa0509f2b0a579f8beb02ac-variantNull\"}"

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "content-type": "application/json",
        "Referer": "https://www.maxidespensa.com.gt/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:153.0) Gecko/20100101 Firefox/153.0"
    }

    def search_products(self, product, from_page, to_page, postal_code=None):

        maxi_parser = ParserMaxiDespensa()

        encode_base64_json = maxi_parser.parser(self.search_variables, product, from_page, to_page)

        # copy so the class-level querystring is never mutated between requests
        querystring = dict(self.querystring)
        querystring['extensions'] = json.dumps({
            "persistedQuery": self.persisted_query,
            "variables": encode_base64_json
        })

        # without postal code Maxi Despensa returns its default prices
        cookies = {}
        if postal_code:
            region = self.get_region(postal_code)
            cookies["vtex_segment"] = encode_vtex_segment(self.sales_channel, region["region_id"], region["seller"])

        base_client = BaseClient()

        response = base_client.get(
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
        sellers = [seller["id"] for seller in (regions[0].get("sellers") or [])] if regions else []
        if not sellers:
            raise NoStoreForPostalCode(postal_code)

        seller = next((s for s in sellers if s.startswith(self.seller_prefix)), sellers[0])
        region = {"region_id": regions[0]["id"], "seller": seller}

        self._region_cache[postal_code] = region
        return region
