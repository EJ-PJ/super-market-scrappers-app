import json
from .base_client import BaseClient
from app.parser.maxi_despensa_search_product_parser import ParserMaxiDespensa


class MaxiDespensaClient:

    # https://msf-api.gta.com.gt/api/products/search
    base_url = "https://www.maxidespensa.com.gt/_v/segment/graphql/v1"

    querystring = {"workspace":"master","maxAge":"short","appsEtag":"remove",
                   "domain":"store","locale":"es-GT","operationName":"productSearchV3",
                   "variables":"{}"}

    # persisted GraphQL query that VTEX expects inside "extensions"
    persisted_query = {"version":1,"sha256Hash":"a96c5ed03ef513568c34b63a4bf8da055ea6296293ee02eadb56e2e895eaffbc",
                       "sender":"vtex.store-resources@0.x","provider":"vtex.search-graphql@0.x"}

    # search variables, sent base64 encoded in extensions["variables"]
    search_variables = "{\"skusFilter\":\"ALL\",\"simulationBehavior\":\"default\",\"installmentCriteria\":\"MAX_WITHOUT_INTEREST\",\"productOriginVtex\":false,\"map\":\"ft\",\"query\":\"monster\",\"orderBy\":\"OrderByScoreDESC\",\"from\":0,\"to\":20,\"selectedFacets\":[{\"key\":\"ft\",\"value\":\"monster\"}],\"fullText\":\"monster\",\"facetsBehavior\":\"Static\",\"categoryTreeBehavior\":\"default\",\"withFacets\":false,\"variant\":\"6aa0509f2b0a579f8beb02ac-variantNull\"}"

    def search_products(self, product, from_page, to_page):

        maxi_parser = ParserMaxiDespensa()

        encode_base64_json = maxi_parser.parser(self.search_variables, product, from_page, to_page)

        # copy so the class-level querystring is never mutated between requests
        querystring = dict(self.querystring)
        querystring['extensions'] = json.dumps({
            "persistedQuery": self.persisted_query,
            "variables": encode_base64_json
        })

        base_client = BaseClient()

        response = base_client.get(
            self.base_url,
            headers={
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive",
                "content-type": "application/json",
                "Referer": "https://www.maxidespensa.com.gt/monster?_q=monster&map=ft",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:153.0) Gecko/20100101 Firefox/153.0"
            },
            params=querystring
        )

        return response.json()
