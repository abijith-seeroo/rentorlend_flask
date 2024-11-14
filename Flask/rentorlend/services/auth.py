from flask import request, jsonify, make_response, current_app
from werkzeug.security import check_password_hash
from functools import wraps
import jwt
import datetime

from models import db, User

# Define a set to hold blacklisted tokens
blacklist = set()

# Token required decorator with blacklist check
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        # Check if the token is in the blacklist
        if token in blacklist:
            return jsonify({'message': 'Token has been revoked! Please log in again.'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

# Login function
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify!', 401, {'WWW-authenticate': 'Basic realm="login required"'})

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response('Could not verify!', 401, {'WWW-authenticate': 'Basic realm="login required"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
            current_app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({
            'message': 'Login successful!',
            'token': token
        }), 200

    return make_response('Could not verify!', 401, {'WWW-authenticate': 'Basic realm="login required"'})

# Logout function
@token_required
def logout(current_user):
    token = request.headers.get('x-access-token')

    # Add the token to the blacklist
    blacklist.add(token)
    return jsonify({'message': 'Successfully logged out!'}), 200
