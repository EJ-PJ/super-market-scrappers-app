from .base_client import BaseClient
from app.parser.maxi_despensa_parser import ParserMaxiDespensa


class MaxiDespensaClient:

    # https://msf-api.gta.com.gt/api/products/search
    base_url = "https://www.maxidespensa.com.gt/_v/segment/graphql/v1"

    body =  ""

    querystring = {"workspace":"master","maxAge":"short","appsEtag":"remove",
                   "domain":"store","locale":"es-GT","operationName":"productSearchV3",
                   "variables":"{}","extensions":"{\"skusFilter\":\"ALL\",\"simulationBehavior\":\"default\",\"installmentCriteria\":\"MAX_WITHOUT_INTEREST\",\"productOriginVtex\":false,\"map\":\"ft\",\"query\":\"monster\",\"orderBy\":\"OrderByScoreDESC\",\"from\":0,\"to\":20,\"selectedFacets\":[{\"key\":\"ft\",\"value\":\"monster\"}],\"fullText\":\"monster\",\"facetsBehavior\":\"Static\",\"categoryTreeBehavior\":\"default\",\"withFacets\":false,\"variant\":\"6aa0509f2b0a579f8beb02ac-variantNull\"}"}

    def search_products(self, product, from_page, to_page):

        maxi_parser = ParserMaxiDespensa()

        encode_base64_json = maxi_parser.parser(self.querystring['extensions'], product, from_page, to_page)

        self.querystring['extensions'] = encode_base64_json

        base_client = BaseClient()

        response = base_client.post(
            self.base_url,
            json=self.body,
            headers={
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive",
                "content-type": "application/json",
                "Cookie": "_fbp=fb.2.1789671262704.754565879863158403.AQYCAQIB; vtex-search-anonymous=6cb1f5f9673e4e0d90848437821c6bdb; checkout.vtex.com=__ofid=544d8c19abaa4a4ea66447d635a3d973; CheckoutOrderFormOwnership=0buoTLo9pREI%2BfyqkkFsqsxKxdwvlhellUSEF7oZZlncKFtGMvuv6o%2B4zv7STxTC8wQyH5oVbA%2FCoBIoljlpS%2FFF6wR4pYDtPpjpMtOiudDT3GZwXc%2Bs7dSX5PkSFgPxbujO3kmcJ9afwUG9yTvXw4SLIdSybU%2FlMHtOFc2cQUwGrpchkoZB38M%2F80RzGJ%2BHhEONBgYlrUxdasKX39tP2CQAvObaDjbk%2FbIv%2FOtV5H7DLproiNuP1PF555%2BYHmNNY8ZF7cENPslUTXqu3S3ZdxRKmoS189ArcE2fXPzsd%2FQZz35YxWLdmL8oEiIopjSWTVQKUw5lwgikClyty3et9vohyVKkURjTtQn0fdufq0qB9f1u94WDNhEptL%2B3foi3PTJikb%2BcYMAUFFgu0KOXvw%3D%3D; vtex_binding_address=bodegagt.myvtex.com/; VtexWorkspace=master%3A-; vtex_session=eyJhbGciOiJFUzI1NiIsImtpZCI6IjdhN2U4ZDdmLWNjNGQtNDY1OS1hNTMyLWRjYmIwZGJiZDVkYiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50LmlkIjpbXSwiaWQiOiIyNjhmZmI5OC1lOTU5LTRmYmItOWQ3My01YjNkMWVhN2IwNzMiLCJ2ZXJzaW9uIjozLCJzdWIiOiJzZXNzaW9uIiwiYWNjb3VudCI6ImJvZGVnYWd0IiwiZXhwIjoxNzkxNDA0MDkxLCJpYXQiOjE3OTA5NzIwOTEsImp0aSI6IjE4NjljNWIxLWY4MzItNDJkZC1hMzhhLTU0ZWRlZWNmZTQxMyIsImlzcyI6InNlc3Npb24vZGF0YS1zaWduZXIifQ.yapHFjnjPNXtcVn4cSgEMmuMxvjJ1DZozsJuIH2HzwZ3h5T6qx6le0meDfIjxNMdUWwoVxByFfiKZrWs0WG0Fw; vtex_segment=eyJjYW1wYWlnbnMiOm51bGwsImNoYW5uZWwiOiIzIiwicHJpY2VUYWJsZXMiOm51bGwsInJlZ2lvbklkIjoiVTFjamQyRnNiV0Z5ZEdkMFltODBPVEk9IiwidXRtX2NhbXBhaWduIjpudWxsLCJ1dG1fc291cmNlIjpudWxsLCJ1dG1pX2NhbXBhaWduIjpudWxsLCJjdXJyZW5jeUNvZGUiOiJHVFEiLCJjdXJyZW5jeVN5bWJvbCI6IlEiLCJjb3VudHJ5Q29kZSI6IkdUTSIsImN1bHR1cmVJbmZvIjoiZXMtR1QiLCJjaGFubmVsUHJpdmFjeSI6InB1YmxpYyIsImZhY2V0cyI6ImFjY2Vzc2NvbnRyb2xsaXN0PXdhbG1hcnRndGJvNDkyOyJ9; vtex-search-session=cb7bdce9387d4251a9402182a38fc9d7; sp-variant=6aa0509f2b0a579f8beb02ac-variantNull; CheckoutLocale=es-GT",
                "Referer": "https://www.maxidespensa.com.gt/monster?_q=monster&map=ft",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:153.0) Gecko/20100101 Firefox/153.0"
            },
            params=self.querystring
        )

        return response.json()
