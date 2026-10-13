from flask import Blueprint, request
from app.services import Products
from app.postal_code import PostalCode

products_bp = Blueprint('routes', __name__)


@products_bp.route('/api/v1/search-products', methods=['GET'])
def search_products():
    body = request.get_json() # Json Body

    # Test if Json body was sent
    if not body:
        return {"error": "JSON data is required"}, 400

    query = body.get("query")

    super_market = body.get("super_market")

    # Test if json has attribute query
    if not query:
        return {"error": "query is required"}, 400

    if not super_market:
        return {"error": "super_market is required"}, 400

    products = Products()

    if super_market == 'maxi_despensa':
        print(body)
        from_quantity = body.get("from")
        print("from_quantity", from_quantity)


        to_quantity = body.get("to")
        print("to_quantity", to_quantity)

        if from_quantity == None:
            return {"error": "from is required"}, 400
        elif to_quantity == None:
            return {"error": "to is required"}, 400
        else:
            # maxi_despensa products
            products.search_products_maxi_despensa(body["query"], int(from_quantity), int(to_quantity))

    elif super_market == 'super_fresh':
        # super_fresh products
        products.search_products_super_fresh(body["query"])

    elif super_market == 'all':
        print(body)
        from_quantity = body.get("from")
        print("from_quantity", from_quantity)


        to_quantity = body.get("to")
        print("to_quantity", to_quantity)

        if from_quantity == None:
            return {"error": "from is required"}, 400
        elif to_quantity == None:
            return {"error": "to is required"}, 400
        else:
            # maxi_despensa products
            products.search_products(body["query"], int(from_quantity), int(to_quantity))
    else:
        return {"data": "super_market not found"}, 400

    result = products.products_

    
    # search_promos test
    """
    from app.parser.promo_parser_maxi_despensa import ParserPromo
    parser_promo = ParserPromo()

    print()
    for product in result["data"]["productSearch"]["products"]:
        promos = parser_promo.extract_promos(product)
        if promos:
            print(product["productName"], [p["label"] for p in promos])
        #promo_result = parser_promo.extract_promos(result)
    print()
    """

    return {"data": result}, 200


@products_bp.route('/api/v1/search-postal-code', methods=['GET'])
def find_postal_code():
    department = request.args.get("department")
    municipality = request.args.get("municipality")
    area = request.args.get("area") # Optional, only needed for municipalities split by zones

    # Test if required query params were sent
    if not department or not municipality:
        return {"error": "department and municipality are required"}, 400

    postal_code = PostalCode()
    result = postal_code.find_postal_code(department, municipality, area)

    # Test if a postal code was found
    if result is None:
        return {"error": "postal code not found"}, 404

    return {
        "department": postal_code.deparment,
        "municipality": postal_code.municipality,
        "area": area,
        "postal_code": result
    }, 200
