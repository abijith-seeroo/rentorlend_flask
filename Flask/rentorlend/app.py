from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask import Flask, request, jsonify, make_response, render_template
import json
import jwt
from functools import wraps
import uuid
from sqlalchemy.exc import IntegrityError
import datetime
from flask_swagger_ui import get_swaggerui_blueprint
from flasgger import Swagger, swag_from


app = Flask(__name__)
Swagger(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:new_password@localhost:5432/rental_database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']='here_is_my_secret_key'


db = SQLAlchemy(app)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'  # Define the location of your JSON spec if using external documentation
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/create_user',methods=['POST','GET'])
def create_user():
    data_create_user= request.get_json()

    hashed_password=generate_password_hash(data_create_user['password'], method='pbkdf2:sha256')
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


@app.route('/update_user/<user_id>', methods=['PUT'])
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


@app.route('/delete_user/<user_id>', methods=['DELETE'])
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


@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_details(user_id):
    try:
        # Query the user by their ID
        user = User.query.get(user_id)

        # If user is not found, return a 404
        if not user:
            return jsonify({"message": "User not found"}), 404

        # Construct the user details response
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

@app.route('/login',methods=['POST','GET'])
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
            app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({
            'message': 'Login successful!',
            'token': token
        }), 200

    return make_response('Could not verify!', 401, {'WWW-authenticate': 'Basic realm="login required"'})




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
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/logout', methods=['POST','GET'])
@token_required
def logout(current_user):
    token = request.headers.get('x-access-token')

    # Add the token to the blacklist
    blacklist.add(token)
    return jsonify({'message': 'Successfully logged out!'}), 200



with open('/home/srodoo/PycharmProjects/scrappy python/lens_rentals/camera.json') as file:
    data = json.load(file)

@app.route("/insert_products", methods=['POST', 'GET'])
def insert_products():
    with app.app_context():
        for item in data:
            # Map JSON fields to Product model fields
            name = item.get("title")
            product_details_link = item.get("product_link")
            price = float(item.get("price", "$0").replace("$", ""))  # Remove "$" and convert to float
            image = item.get("image_url")
            # category_id = 1  # Default or fetched value
            # brand_id = 1  # Default or fetched value
            # camera_type_id = 1  # Default or fetched value
            # lens_type_id = 1  # Default or fetched value

            # Create a new Product instance
            new_product = Product(
                name=name,
                product_details_link=product_details_link,
                price=price,
                availability=True,
                location_latitude=None,  # Set these if available in JSON
                location_longitude=None,
                image=image,
                vendor_name="Default Vendor",  # Default or fetched value
                category_id=None,
                is_featured=False,
                is_popular=False,
                brand_id=None,
                camera_type_id=None,
                lens_type_id=None
            )

            # Add the new product to the session
            db.session.add(new_product)

        # Commit all products to the database at once
        db.session.commit()

    return jsonify({"message": "Products inserted successfully!"}), 201

@app.route('/update_product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), 400

    # Update fields if they are present in the request
    product.name = data.get('name', product.name)
    product.price = data.get('price', product.price)
    product.availability = data.get('availability', product.availability)
    product.vendor_name = data.get('vendor_name', product.vendor_name)
    product.image = data.get('image', product.image)
    product.category_id = data.get('category_id', product.category_id)
    product.is_featured = data.get('is_featured', product.is_featured)
    product.is_popular = data.get('is_popular', product.is_popular)
    product.brand_id = data.get('brand_id', product.brand_id)
    product.camera_type_id = data.get('camera_type_id', product.camera_type_id)
    product.lens_type_id = data.get('lens_type_id', product.lens_type_id)

    try:
        db.session.commit()
        return jsonify({"message": "Product updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to update product", "error": str(e)}), 500


@app.route('/delete/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        # Query the product by its ID
        product = Product.query.get(product_id)

        # If product is not found, return a 404
        if not product:
            return jsonify({"message": "Product not found"}), 404

        # Delete the product
        db.session.delete(product)
        db.session.commit()

        return jsonify({"message": "Product deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to delete product", "error": str(e)}), 500



@app.route("/products_list", methods=['GET'])
def get_products():
    with app.app_context():
        # Query all products
        products = Product.query.all()

        # Convert each product to a dictionary
        products_list = []
        for product in products:
            product_data = {
                "product_id": product.product_id,
                "name": product.name,
                "user_id": product.user_id,
                "product_details_link": product.product_details_link,
                "price": product.price,
                "availability": product.availability,
                "expiry_date": product.expiry_date,
                "location_latitude": product.location_latitude,
                "location_longitude": product.location_longitude,
                "image": product.image,
                "vendor_name": product.vendor_name,
                "category_id": product.category_id,
                "created_date": product.created_date,
                "updated_date": product.updated_date,
                "is_featured": product.is_featured,
                "is_popular": product.is_popular,
                "brand_id": product.brand_id,
                "camera_type_id": product.camera_type_id,
                "lens_type_id": product.lens_type_id
            }
            products_list.append(product_data)

        # Return the list of products as JSON
        return jsonify(products_list), 200


@app.route('/search_products', methods=['GET'])
def search_products():
    query = Product.query

    # Get search parameters from the request
    name = request.args.get('name')


    # Filter by name
    if name:
        query = query.filter(Product.name.ilike(f'%{name}%'))

    # Filter by price range


    # Execute the query and get results
    products = query.all()

    # Convert each product to a dictionary
    products_list = [
        {
            "product_id": product.product_id,
            "name": product.name,
            "user_id": product.user_id,
            "product_details_link": product.product_details_link,
            "price": product.price,
            "availability": product.availability,
            "expiry_date": product.expiry_date,
            "location_latitude": product.location_latitude,
            "location_longitude": product.location_longitude,
            "image": product.image,
            "vendor_name": product.vendor_name,
            "category_id": product.category_id,
            "created_date": product.created_date,
            "updated_date": product.updated_date,
            "is_featured": product.is_featured,
            "is_popular": product.is_popular,
            "brand_id": product.brand_id,
            "camera_type_id": product.camera_type_id,
            "lens_type_id": product.lens_type_id
        } for product in products
    ]

    # Return the list of products as JSON
    return jsonify(products_list), 200


# Route to create a product category
@app.route('/create_product_category', methods=['POST'])
def create_product_category():
    data = request.get_json()

    # Extract data from the request
    name = data.get('name')
    description = data.get('description')

    # Create a new ProductCategory instance
    new_category = ProductCategory(name=name, description=description)

    # Add and commit the new category to the database
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

@app.route('/update_product_category/<int:category_id>', methods=['PUT'])
def update_product_category(category_id):
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    category = ProductCategory.query.get(category_id)
    if not category:
        return jsonify({"message": "Category not found"}), 404

    # Update fields if provided
    if name:
        category.name = name
    if description:
        category.description = description

    try:
        db.session.commit()
        return jsonify({"message": "Product category updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to update category", "error": str(e)}), 500

@app.route('/delete_product_category/<int:category_id>', methods=['DELETE'])
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

@app.route('/product_categories', methods=['GET'])
def get_product_categories():
    try:
        # Query all product categories
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


@app.route('/product/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    try:
        # Query the product by its ID
        product = Product.query.get(product_id)

        if not product:
            return jsonify({"message": "Product not found"}), 404

        # Construct the product details response
        product_details = {
            "product_id": product.product_id,
            "name": product.name,
            "price": product.price,
            "availability": product.availability,
            "expiry_date": product.expiry_date,
            "location_latitude": product.location_latitude,
            "location_longitude": product.location_longitude,
            "image": product.image,
            "vendor_name": product.vendor_name,
            "category_id": product.category_id,
            "brand_id": product.brand_id,
            "camera_type_id": product.camera_type_id,
            "lens_type_id": product.lens_type_id,
            "created_date": product.created_date,
            "updated_date": product.updated_date,
            "is_featured": product.is_featured,
            "is_popular": product.is_popular
        }

        return jsonify(product_details), 200

    except Exception as e:
        return jsonify({"message": "Failed to retrieve product details", "error": str(e)}), 500


@app.route('/popular_products', methods=['GET'])
def get_popular_products():
    try:
        # Query all products where is_popular is True
        popular_products = Product.query.filter_by(is_popular=True).all()

        # Format the list of popular products
        popular_product_list = [
            {
                "product_id": product.product_id,
                "name": product.name,
                "price": product.price,
                "availability": product.availability,
                "image": product.image,
                "vendor_name": product.vendor_name,
                "category_id": product.category_id,
                "created_date": product.created_date,
                "updated_date": product.updated_date
            } for product in popular_products
        ]

        return jsonify(popular_product_list), 200

    except Exception as e:
        return jsonify({"message": "Failed to retrieve popular products", "error": str(e)}), 500


@app.route('/featured_products', methods=['GET'])
def get_featured_products():
    try:
        # Query all products where is_featured is True
        featured_products = Product.query.filter_by(is_featured=True).all()

        # Format the list of featured products
        featured_product_list = [
            {
                "product_id": product.product_id,
                "name": product.name,
                "price": product.price,
                "availability": product.availability,
                "image": product.image,
                "vendor_name": product.vendor_name,
                "category_id": product.category_id,
                "created_date": product.created_date,
                "updated_date": product.updated_date
            } for product in featured_products
        ]

        return jsonify(featured_product_list), 200

    except Exception as e:
        return jsonify({"message": "Failed to retrieve featured products", "error": str(e)}), 500


@app.route('/products/brand/<int:brand_id>', methods=['GET'])
def get_products_by_brand(brand_id):
    try:
        # Query products by brand_id
        products = Product.query.filter_by(brand_id=brand_id).all()

        # If no products are found for the brand, return a 404
        if not products:
            return jsonify({"message": "No products found for the specified brand"}), 404

        # Format the list of products
        product_list = [
            {
                "product_id": product.product_id,
                "name": product.name,
                "price": product.price,
                "availability": product.availability,
                "image": product.image,
                "vendor_name": product.vendor_name,
                "category_id": product.category_id,
                "created_date": product.created_date,
                "updated_date": product.updated_date
            } for product in products
        ]

        return jsonify(product_list), 200

    except Exception as e:
        return jsonify({"message": "Failed to retrieve products for the specified brand", "error": str(e)}), 500


@app.route('/products/camera_type/<int:camera_type_id>', methods=['GET'])
def get_products_by_camera_type(camera_type_id):
    try:
        # Query products by camera_type_id
        products = Product.query.filter_by(camera_type_id=camera_type_id).all()

        # If no products are found for the camera type, return a 404
        if not products:
            return jsonify({"message": "No products found for the specified camera type"}), 404

        # Format the list of products
        product_list = [
            {
                "product_id": product.product_id,
                "name": product.name,
                "price": product.price,
                "availability": product.availability,
                "image": product.image,
                "vendor_name": product.vendor_name,
                "category_id": product.category_id,
                "created_date": product.created_date,
                "updated_date": product.updated_date
            } for product in products
        ]

        return jsonify(product_list), 200

    except Exception as e:
        return jsonify({"message": "Failed to retrieve products for the specified camera type", "error": str(e)}), 500


@app.route('/products/lens_type/<int:lens_type_id>', methods=['GET'])
def get_products_by_lens_type(lens_type_id):
    try:
        # Query products by lens_type_id
        products = Product.query.filter_by(lens_type_id=lens_type_id).all()

        # If no products are found for the lens type, return a 404
        if not products:
            return jsonify({"message": "No products found for the specified lens type"}), 404

        # Format the list of products
        product_list = [
            {
                "product_id": product.product_id,
                "name": product.name,
                "price": product.price,
                "availability": product.availability,
                "image": product.image,
                "vendor_name": product.vendor_name,
                "category_id": product.category_id,
                "created_date": product.created_date,
                "updated_date": product.updated_date
            } for product in products
        ]

        return jsonify(product_list), 200

    except Exception as e:
        return jsonify({"message": "Failed to retrieve products for the specified lens type", "error": str(e)}), 500

@app.route('/products/filtration', methods=['GET'])
def get_products_filtration():
    try:
        # Get query parameters
        lens_type_id = request.args.get('lens_type_id', type=int)
        camera_type_id = request.args.get('camera_type_id', type=int)
        brand_id = request.args.get('brand_id', type=int)

        # Base query
        query = Product.query

        # Apply filters if parameters are provided
        if lens_type_id is not None:
            query = query.filter_by(lens_type_id=lens_type_id)
        if camera_type_id is not None:
            query = query.filter_by(camera_type_id=camera_type_id)
        if brand_id is not None:
            query = query.filter_by(brand_id=brand_id)

        # Execute the query
        products = query.all()

        # If no products are found, return a 404
        if not products:
            return jsonify({"message": "No products found for the specified criteria"}), 404

        # Format the list of products
        product_list = [
            {
                "product_id": product.product_id,
                "name": product.name,
                "price": product.price,
                "availability": product.availability,
                "image": product.image,
                "vendor_name": product.vendor_name,
                "category_id": product.category_id,
                "created_date": product.created_date,
                "updated_date": product.updated_date
            } for product in products
        ]

        return jsonify(product_list), 200

    except Exception as e:
        return jsonify({"message": "Failed to retrieve products", "error": str(e)}), 500

@app.route('/brands', methods=['GET'])
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
@app.route('/create_brand_name', methods=['POST'])
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


@app.route('/update_brand/<int:brand_id>', methods=['PUT'])
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


@app.route('/delete_brand/<int:brand_id>', methods=['DELETE'])
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


# Route to create camera type
@app.route('/create_camera_type', methods=['POST'])
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
@app.route('/update_camera_type/<int:camera_type_id>', methods=['PUT'])
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
@app.route('/delete_camera_type/<int:camera_type_id>', methods=['DELETE'])
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


# Route to create lens type
@app.route('/create_lens_type', methods=['POST'])
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

@app.route('/update_lens_type/<int:lens_type_id>', methods=['PUT'])
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

@app.route('/delete_lens_type/<int:lens_type_id>', methods=['DELETE'])
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

@app.route('/home', methods=['GET'])
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


@app.route('/enquiry', methods=['POST'])
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


@app.route('/enquiry/<int:enquiry_id>', methods=['PUT'])
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


@app.route('/delete/enquiry/<int:enquiry_id>', methods=['DELETE'])
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


@app.route('/enquiries', methods=['GET'])
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


@app.route('/enquiry/details/<int:enquiry_id>', methods=['GET'])
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

# User table
class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile_no = db.Column(db.String(15))
    is_vendor = db.Column(db.Boolean, default=False)
    is_customer = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(120), nullable=False)
    created_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_date = db.Column(db.DateTime, onupdate=db.func.current_timestamp())
    user_image = db.Column(db.String(250))
    opening_time = db.Column(db.Time)
    closing_time = db.Column(db.Time)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

# ProductCategory table
class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True,nullable=False)
    description = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_date = db.Column(db.DateTime, onupdate=db.func.current_timestamp())

# Product table
class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    product_details_link = db.Column(db.String(250))
    price = db.Column(db.Float)
    availability = db.Column(db.Boolean, default=False)
    expiry_date = db.Column(db.Date)
    location_latitude = db.Column(db.Float)
    location_longitude = db.Column(db.Float)
    image = db.Column(db.String(250))
    vendor_name = db.Column(db.String(50))
    category_id = db.Column(db.Integer, db.ForeignKey('product_category.category_id'))
    created_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_date = db.Column(db.DateTime, onupdate=db.func.current_timestamp())
    is_featured = db.Column(db.Boolean, default=False)
    is_popular = db.Column(db.Boolean, default=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.brand_id'))
    camera_type_id = db.Column(db.Integer, db.ForeignKey('camera_type.camera_type_id'))
    lens_type_id = db.Column(db.Integer, db.ForeignKey('lens_type.lens_type_id'))

# Enquiry table
class Enquiry(db.Model):
    __tablename__ = 'enquiry'
    enquiry_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    status = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_date = db.Column(db.DateTime, onupdate=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    enquired_date = db.Column(db.DateTime)
    requested_date = db.Column(db.DateTime)

# Brand table
class Brand(db.Model):
    __tablename__ = 'brand'
    brand_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),unique=True)
    description = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_date = db.Column(db.DateTime, onupdate=db.func.current_timestamp())


# CameraType table
class CameraType(db.Model):
    __tablename__ = 'camera_type'
    camera_type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),unique=True)
    description = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_date = db.Column(db.DateTime, onupdate=db.func.current_timestamp())

# LensType table
class LensType(db.Model):
    __tablename__ = 'lens_type'
    lens_type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),unique=True)
    description = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_date = db.Column(db.DateTime, onupdate=db.func.current_timestamp())

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


if __name__ == '__main__':
    # with app.app_context():
        # db.drop_all()
        # db.create_all()  # Creates all tables defined
    app.run(debug=True)