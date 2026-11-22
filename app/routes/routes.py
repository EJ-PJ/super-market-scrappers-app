from flask import Blueprint, request
from app.services import Products, STORES
from app.postal_code import PostalCode

products_bp = Blueprint('routes', __name__)

MAX_PAGE_SIZE = 50


# GET /api/v1/products?q=leche&stores=maxi_despensa,super_fresh&page=1&page_size=20&postal_code=1010
@products_bp.route('/api/v1/products', methods=['GET'])
def search_products():
    query = (request.args.get("q") or "").strip()
    if not query:
        return {"error": "q is required"}, 400

    # stores is optional, without it search in every store
    stores_param = request.args.get("stores")
    if stores_param:
        store_ids = list(dict.fromkeys(s.strip() for s in stores_param.split(",") if s.strip()))
    else:
        store_ids = list(STORES)

    unknown = [s for s in store_ids if s not in STORES]
    if unknown or not store_ids:
        return {"error": f"unknown stores: {', '.join(unknown)}",
                "available_stores": list(STORES)}, 400

    page = to_int(request.args.get("page", "1"))
    page_size = to_int(request.args.get("page_size", "20"))
    if page is None or page < 1:
        return {"error": "page must be an integer >= 1"}, 400
    if page_size is None or not 1 <= page_size <= MAX_PAGE_SIZE:
        return {"error": f"page_size must be an integer between 1 and {MAX_PAGE_SIZE}"}, 400

    # optional, from /api/v1/search-postal-code (e.g. 1010 = Guatemala, Zona 10)
    postal_code = (request.args.get("postal_code") or "").strip() or None
    if postal_code and not postal_code.isdigit():
        return {"error": "postal_code must contain only digits"}, 400

    return Products().search_products(query, store_ids, page, page_size, postal_code), 200


def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@products_bp.route('/api/v1/stores', methods=['GET'])
def list_stores():
    return {"stores": [{"id": store_id, "name": store["name"]} for store_id, store in STORES.items()]}, 200


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
