from flask import Blueprint, request, jsonify
from models import db, LensType


lens_bp = Blueprint('lens_bp', __name__)

# Route to create lens type
@lens_bp.route('/create_lens_type', methods=['POST'])
def create_lens_type():
    data = request.get_json()

    # Extract data from the request
    name = data.get('name')
    description = data.get('description')

    # Create a new ProductCategory instance
    new_type = LensType(name=name, description=description)

    # Add and commit the new category to the database
    try:
        db.session.add(new_type)
        db.session.commit()
        return jsonify({
            "message": "New Lens Type Added successfully",
            "brand_id": new_type.lens_type_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to create Camera Type", "error": str(e)}), 500

@lens_bp.route('/update_lens_type/<int:lens_type_id>', methods=['PUT'])
def update_lens_type(lens_type_id):
    data = request.get_json()

    # Extract the new data
    name = data.get('name')
    description = data.get('description')

    # Find the lens type by id
    lens_type = LensType.query.get(lens_type_id)

    if lens_type:
        # Update the values
        if name:
            lens_type.name = name
        if description:
            lens_type.description = description

        try:
            db.session.commit()
            return jsonify({
                "message": "Lens Type updated successfully",
                "lens_type_id": lens_type.lens_type_id
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Failed to update Lens Type", "error": str(e)}), 500
    else:
        return jsonify({"message": "Lens Type not found"}), 404

@lens_bp.route('/delete_lens_type/<int:lens_type_id>', methods=['DELETE'])
def delete_lens_type(lens_type_id):
    # Find the lens type by id
    lens_type = LensType.query.get(lens_type_id)

    if lens_type:
        try:
            db.session.delete(lens_type)
            db.session.commit()
            return jsonify({
                "message": "Lens Type deleted successfully",
                "lens_type_id": lens_type.lens_type_id
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Failed to delete Lens Type", "error": str(e)}), 500
    else:
        return jsonify({"message": "Lens Type not found"}), 404