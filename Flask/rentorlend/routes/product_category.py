from flask import Blueprint, request, jsonify
from models import db, ProductCategory

product_category_bp = Blueprint('product_category_bp', __name__)

@product_category_bp.route('/create_product_category', methods=['POST'])
def create_product_category():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    new_category = ProductCategory(name=name, description=description)

    try:
        db.session.add(new_category)
        db.session.commit()
        return jsonify({
            "message": "Product category created successfully",
            "category_id": new_category.category_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to create category", "error": str(e)}), 500

@product_category_bp.route('/update_product_category/<int:category_id>', methods=['PUT'])
def update_product_category(category_id):
    data = request.get_json()
    category = ProductCategory.query.get(category_id)

    if not category:
        return jsonify({"message": "Category not found"}), 404

    category.name = data.get('name', category.name)
    category.description = data.get('description', category.description)

    try:
        db.session.commit()
        return jsonify({"message": "Product category updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to update category", "error": str(e)}), 500

@product_category_bp.route('/delete_product_category/<int:category_id>', methods=['DELETE'])
def delete_product_category(category_id):
    category = ProductCategory.query.get(category_id)

    if not category:
        return jsonify({"message": "Category not found"}), 404

    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message": "Product category deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to delete category", "error": str(e)}), 500

@product_category_bp.route('/product_categories', methods=['GET'])
def get_product_categories():
    try:
        categories = ProductCategory.query.all()
        category_list = [
            {
                "category_id": category.category_id,
                "name": category.name,
                "description": category.description
            } for category in categories
        ]

        return jsonify(category_list), 200
    except Exception as e:
        return jsonify({"message": "Failed to retrieve product categories", "error": str(e)}), 500
