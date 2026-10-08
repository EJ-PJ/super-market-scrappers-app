class SuperFreshScrapperProduct:

    def product_parser(self, products : dict):
        sp_products = {"super_fresh" : {
                    "products" : []
                    }
                }
        i = 0
        for product in products['products']:
            product_desp = {
                    "description" : "",
                    "price" : "",
                    "price_offer": "",
                    "img" : "",
                    "offeHighlight": [],
                    "url" : ""
			} 
            # adding description
            product_desp["description"] = product.get("description")
            # adding price
            product_desp['price'] = product.get("price")
            # adding price_offer
            product_desp['price_offer'] = product.get("offer", {}).get("price")
            # adding img
            product_desp['img'] = product.get("images", [{}])[0].get("url")
            # adding bar code
            bar_code = product.get('barcode')
            url_p = f"https://www.misuperfresh.com.gt/product/{bar_code}"
            product_desp['url'] = url_p

            # adding product
            sp_products['super_fresh']['products'].append(product_desp)

        return sp_products
