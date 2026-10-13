class MergeProducts:

    def merge_products(self, *super_markets: dict, super_market_names : list):
        data = {}

        i = 0
        for super_market in super_markets:
            super_market_name = super_market_names[i]
            data[super_market_name] = super_market[super_market_name]
            i += 1

        return data
