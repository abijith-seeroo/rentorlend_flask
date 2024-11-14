from flask import Blueprint, request, jsonify
from models import db, Enquiry


enquiry_bp = Blueprint('enquiry_bp', __name__)

@enquiry_bp.route('/enquiry', methods=['POST'])
def create_enquiry():
    data = request.get_json()

    # Check if required data is provided
    if not data or not data.get('name') or not data.get('description'):
        return jsonify({"message": "Name and description are required"}), 400

    try:
        # Create a new enquiry instance
        new_enquiry = Enquiry(
            name=data['name'],
            description=data['description'],
            status=data.get('status', False),  # Default status to False if not provided
            user_id=data.get('user_id'),  # Assuming each enquiry is linked to a user
            enquired_date=data.get('enquired_date'),
            requested_date=data.get('requested_date')
        )

        # Add and commit the new enquiry to the database
        db.session.add(new_enquiry)
        db.session.commit()

        return jsonify({"message": "Enquiry created successfully", "enquiry_id": new_enquiry.enquiry_id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to create enquiry", "error": str(e)}), 500


@enquiry_bp.route('/enquiry/<int:enquiry_id>', methods=['PUT'])
def update_enquiry(enquiry_id):
    try:
        # Query the enquiry by its ID
        enquiry = Enquiry.query.get(enquiry_id)

        # If enquiry is not found, return a 404
        if not enquiry:
            return jsonify({"message": "Enquiry not found"}), 404

        # Get the updated data from the request
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400

        # Update fields if provided in the request
        enquiry.name = data.get('name', enquiry.name)
        enquiry.description = data.get('description', enquiry.description)
        enquiry.status = data.get('status', enquiry.status)
        enquiry.user_id = data.get('user_id', enquiry.user_id)
        enquiry.enquired_date = data.get('enquired_date', enquiry.enquired_date)
        enquiry.requested_date = data.get('requested_date', enquiry.requested_date)

        # Commit the changes to the database
        db.session.commit()

        return jsonify({"message": "Enquiry updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to update enquiry", "error": str(e)}), 500


@enquiry_bp.route('/delete/enquiry/<int:enquiry_id>', methods=['DELETE'])
def delete_enquiry(enquiry_id):
    try:
        # Query the enquiry by its ID
        enquiry = Enquiry.query.get(enquiry_id)

        # If enquiry is not found, return a 404
        if not enquiry:
            return jsonify({"message": "Enquiry not found"}), 404

        # Delete the enquiry
        db.session.delete(enquiry)
        db.session.commit()

        return jsonify({"message": "Enquiry deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to delete enquiry", "error": str(e)}), 500


@enquiry_bp.route('/enquiries', methods=['GET'])
def get_enquiries():
    try:
        # Query all enquiries
        enquiries = Enquiry.query.all()

        # Format the list of enquiries
        enquiry_list = [
            {
                "enquiry_id": enquiry.enquiry_id,
                "name": enquiry.name,
                "description": enquiry.description,
                "status": enquiry.status,
                "user_id": enquiry.user_id,
                "enquired_date": enquiry.enquired_date,
                "requested_date": enquiry.requested_date,
                "created_date": enquiry.created_date,
                "updated_date": enquiry.updated_date
            } for enquiry in enquiries
        ]

        return jsonify(enquiry_list), 200

    except Exception as e:
        return jsonify({"message": "Failed to retrieve enquiries", "error": str(e)}), 500


@enquiry_bp.route('/enquiry/details/<int:enquiry_id>', methods=['GET'])
def get_enquiry_details(enquiry_id):
    try:
        # Query the enquiry by its ID
        enquiry = Enquiry.query.get(enquiry_id)

        # If enquiry is not found, return a 404
        if not enquiry:
            return jsonify({"message": "Enquiry not found"}), 404

        # Construct the enquiry details response
        enquiry_details = {
            "enquiry_id": enquiry.enquiry_id,
            "name": enquiry.name,
            "description": enquiry.description,
            "status": enquiry.status,
            "user_id": enquiry.user_id,
            "enquired_date": enquiry.enquired_date,
            "requested_date": enquiry.requested_date,
            "created_date": enquiry.created_date,
            "updated_date": enquiry.updated_date
        }

        return jsonify(enquiry_details), 200

    except Exception as e:
        return jsonify({"message": "Failed to retrieve enquiry details", "error": str(e)}), 500