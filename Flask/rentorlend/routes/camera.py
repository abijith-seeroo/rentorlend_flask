from flask import Blueprint, request, jsonify
from models import db, CameraType


camera_bp = Blueprint('camera_bp', __name__)


# Route to create camera type
@camera_bp.route('/create_camera_type', methods=['POST'])
def create_camera_type():
    data = request.get_json()

    # Extract data from the request
    name = data.get('name')
    description = data.get('description')

    # Create a new ProductCategory instance
    new_type = CameraType(name=name, description=description)

    # Add and commit the new category to the database
    try:
        db.session.add(new_type)
        db.session.commit()
        return jsonify({
            "message": "New Camera Type Added successfully",
            "brand_id": new_type.camera_type_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to create Camera Type", "error": str(e)}), 500

# Route to update a camera type
@camera_bp.route('/update_camera_type/<int:camera_type_id>', methods=['PUT'])
def update_camera_type(camera_type_id):
    data = request.get_json()

    # Fetch the camera type by ID
    camera_type = CameraType.query.get(camera_type_id)
    if not camera_type:
        return jsonify({"message": "Camera Type not found"}), 404

    # Update fields if they are provided in the request
    camera_type.name = data.get('name', camera_type.name)
    camera_type.description = data.get('description', camera_type.description)

    try:
        db.session.commit()
        return jsonify({
            "message": "Camera Type updated successfully",
            "camera_type_id": camera_type.camera_type_id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to update Camera Type", "error": str(e)}), 500

# Route to delete a camera type
@camera_bp.route('/delete_camera_type/<int:camera_type_id>', methods=['DELETE'])
def delete_camera_type(camera_type_id):
    # Fetch the camera type by ID
    camera_type = CameraType.query.get(camera_type_id)
    if not camera_type:
        return jsonify({"message": "Camera Type not found"}), 404

    try:
        db.session.delete(camera_type)
        db.session.commit()
        return jsonify({"message": "Camera Type deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to delete Camera Type", "error": str(e)}), 500
