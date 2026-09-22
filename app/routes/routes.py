from flask import Blueprint, request
from app.services import Products

products_bp = Blueprint('routes', __name__)


@products_bp.route('/search', methods=['GET'])
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
