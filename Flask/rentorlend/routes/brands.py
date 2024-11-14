from flask import Blueprint, request, jsonify
from models import db, Brand


brands_bp = Blueprint('brands_bp', __name__)


@brands_bp.route('/brands', methods=['GET'])
def get_brands():
    try:
        # Query all brands
        brands = Brand.query.all()

        # Format the list of brands
        brand_list = [
            {
                "brand_id": brand.brand_id,
                "name": brand.name,
                "description": brand.description,
                "created_date": brand.created_date,
                "updated_date": brand.updated_date
            } for brand in brands
        ]

        return jsonify(brand_list), 200

    except Exception as e:
        return jsonify({"message": "Failed to retrieve brands", "error": str(e)}), 500

# Route to create a brand
@brands_bp.route('/create_brand_name', methods=['POST'])
def create_brand_name():
    data = request.get_json()

    # Extract data from the request
    name = data.get('name')
    description = data.get('description')

    # Create a new ProductCategory instance
    new_brand = Brand(name=name, description=description)

    # Add and commit the new category to the database
    try:
        db.session.add(new_brand)
        db.session.commit()
        return jsonify({
            "message": "New Brand Name Added successfully",
            "brand_id": new_brand.brand_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to create brand name", "error": str(e)}), 500

@brands_bp.route('/update_brand/<int:brand_id>', methods=['PUT'])
def update_brand(brand_id):
    data = request.get_json()
    brand = Brand.query.get(brand_id)

    if not brand:
        return jsonify({"message": "Brand not found"}), 404

    # Update brand details
    brand.name = data.get('name', brand.name)
    brand.description = data.get('description', brand.description)
    brand.updated_date = db.func.current_timestamp()

    try:
        db.session.commit()
        return jsonify({"message": "Brand updated successfully", "brand_id": brand.brand_id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to update brand", "error": str(e)}), 500

@brands_bp.route('/delete_brand/<int:brand_id>', methods=['DELETE'])
def delete_brand(brand_id):
    brand = Brand.query.get(brand_id)

    if not brand:
        return jsonify({"message": "Brand not found"}), 404

    try:
        db.session.delete(brand)
        db.session.commit()
        return jsonify({"message": "Brand deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to delete brand", "error": str(e)}), 500