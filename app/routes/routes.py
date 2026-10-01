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

    # Test if json has attribute query
    if not query:
        return {"error": "query is required"}, 400

    # print("query:", query)

    products = Products()

    products.search_products(body["query"])

    # print("products:", products.product_superfresh)

    result = products.product_super_fresh["products"]

    # print(result)

    return {"products": result}, 200


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
