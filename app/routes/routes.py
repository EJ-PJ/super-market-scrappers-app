from flask import Blueprint, request
from app.services import Products

products_bp = Blueprint('routes', __name__)


@products_bp.route('/search', methods=['GET'])
def search_products():
    data = request.get_json()

    if not data:
        return {"error": "JSON body is required"}, 400

    query = data.get("query")

    if not query:
        return {"error": "query is required"}, 400

    # print("query:", query)

    products = Products()

    products.search_products(data["query"])

    # print("products:", products.product_superfresh)

    result = products.product_superfresh["products"]

    # print(result)

    return {"products": result}, 200
