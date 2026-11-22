import json, base64

class ParserMaxiDespensa:

    def parser(self, extension: str, product: str, from_: int, to_: int):
        # convert string into dict
        json_res = json.loads(extension)
        
        # changing json value product
        json_res['query'] = product

        # changing json value from page
        json_res['from'] = from_

        # changing json value to page
        json_res['to'] = to_

        # changing json value product
        json_res['selectedFacets'][0]['value'] = product

        # changing json value product
        json_res['fullText'] = product

        json_res_str = json.dumps(json_res)

        encoded_json = base64.b64encode(json_res_str.encode("utf-8"))

        json_str = encoded_json.decode('utf-8')

        return json_str
