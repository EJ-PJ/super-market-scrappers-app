class SuperFreshScrapperProduct:

    def product_parser(self, products : dict):
        sp_products = {"super_fresh" : {
                    "products" : []
                    }
                }

        for product in products['products']:
            product_desp = {
                    "description" : "",
                    "price" : "",
                    "price_offer": "",
                    "img" : "",
                    "offerHighlight": [],
                    "url" : "",
                    "category" : {
                        "name" : "",
                        "subcategory" : {
                            "name" : ""
                        }
                    }
			} 
            # adding description
            product_desp["description"] = product.get("description")
            # adding price
            product_desp['price'] = product.get("price")
            # adding price_offer
            product_desp['price_offer'] = product.get("offer", {}).get("price")
            # adding img
            product_desp['img'] = product.get("images", [{}])[0].get("url")
            # adding category name
            product_desp['category']['name'] = self.safe_get(product, "subcategory", "name") 
            # adding subcategory name
            product_desp['category']['subcategory']['name'] = self.safe_get(product, "subcategory", "category", "name") 
            # adding bar code0
            bar_code = product.get('barcode')
            url_p = f"https://www.misuperfresh.com.gt/product/{bar_code}"
            product_desp['url'] = url_p

            # adding product
            sp_products['super_fresh']['products'].append(product_desp)

        return sp_products


    def safe_get(self, data, *keys, default=None):
        for key in keys:
            try:
                data = data[key]
            except (KeyError, IndexError, TypeError):
                return default
        return data
