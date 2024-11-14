from flask import Blueprint, jsonify
from models import Brand, Product, ProductCategory

home_page_bp = Blueprint('home_page_bp', __name__)

@home_page_bp.route('/home', methods=['GET'])
def get_home_data():
    try:
        # Query brands
        brands = Brand.query.all()
        brand_list = [{"brand_id": brand.brand_id, "name": brand.name} for brand in brands]

        # Query featured products
        featured_products = Product.query.filter_by(is_featured=True).all()
        featured_product_list = [{
            "product_id": product.product_id,
            "name": product.name,
            "price": product.price,
            "image": product.image
        } for product in featured_products]

        # Query popular products
        popular_products = Product.query.filter_by(is_popular=True).all()
        popular_product_list = [{
            "product_id": product.product_id,
            "name": product.name,
            "price": product.price,
            "image": product.image
        } for product in popular_products]

        # Query categories
        categories = ProductCategory.query.all()
        category_list = [{"category_id": category.category_id, "name": category.name} for category in categories]

        # Create response
        home_data = {
            "brands": brand_list,
            "featured_products": featured_product_list,
            "popular_products": popular_product_list,
            "categories": category_list
        }

        return jsonify(home_data), 200

    except Exception as e:
        return jsonify({"message": "Failed to retrieve home page data", "error": str(e)}), 500
