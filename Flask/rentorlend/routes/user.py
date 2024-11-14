from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
import uuid
from models import db, User

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/create_user', methods=['POST'])
def create_user():
    data_create_user = request.get_json()

    hashed_password = generate_password_hash(data_create_user['password'], method='pbkdf2:sha256')
    new_user = User(
        public_id=str(uuid.uuid4()),
        name=data_create_user['name'],
        email=data_create_user['email'],
        mobile_no=data_create_user['mobile_no'],
        is_vendor=data_create_user['is_vendor'],
        is_customer=data_create_user['is_customer'],
        is_admin=data_create_user['is_admin'],
        password=hashed_password,
        user_image=data_create_user['user_image'],
        latitude=data_create_user['latitude'],
        longitude=data_create_user['longitude']
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'New user has been created!'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'An error occurred, please try again.'}), 500


@user_bp.route('/update_user/<user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.filter_by(user_id=user_id).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    data_update_user = request.get_json()

    # Update fields if provided in the request
    user.name = data_update_user.get('name', user.name)
    user.email = data_update_user.get('email', user.email)
    user.mobile_no = data_update_user.get('mobile_no', user.mobile_no)
    user.is_vendor = data_update_user.get('is_vendor', user.is_vendor)
    user.is_customer = data_update_user.get('is_customer', user.is_customer)
    user.is_admin = data_update_user.get('is_admin', user.is_admin)
    user.password = data_update_user.get('password', user.password)  # If password is updated, you may hash it.
    user.user_image = data_update_user.get('user_image', user.user_image)
    user.latitude = data_update_user.get('latitude', user.latitude)
    user.longitude = data_update_user.get('longitude', user.longitude)

    try:
        db.session.commit()
        return jsonify({"message": "User updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to update user", "error": str(e)}), 500


@user_bp.route('/delete_user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.filter_by(user_id=user_id).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to delete user", "error": str(e)}), 500


@user_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_details(user_id):
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({"message": "User not found"}), 404

        user_details = {
            "user_id": user.user_id,
            "public_id": user.public_id,
            "name": user.name,
            "email": user.email,
            "mobile_no": user.mobile_no,
            "is_vendor": user.is_vendor,
            "is_customer": user.is_customer,
            "is_admin": user.is_admin,
            "created_date": user.created_date,
            "updated_date": user.updated_date,
            "user_image": user.user_image,
            "latitude": user.latitude,
            "longitude": user.longitude
        }

        return jsonify(user_details), 200

    except Exception as e:
        return jsonify({"message": "Failed to retrieve user details", "error": str(e)}), 500
