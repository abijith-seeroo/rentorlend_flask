from flask import Blueprint, request, jsonify, current_app
from models import db, Product
import json

products_bp = Blueprint('products_bp', __name__)

# Load data from file (assuming a static file for initial data)
with open('/home/srodoo/PycharmProjects/scrappy python/lens_rentals/camera.json') as file:
    data = json.load(file)

@products_bp.route("/insert_products", methods=['POST', 'GET'])
def insert_products():
    with current_app.app_context():
        for item in data:
            # Map JSON fields to Product model fields
            name = item.get("title")
            product_details_link = item.get("product_link")
            price = float(item.get("price", "$0").replace("$", ""))  # Remove "$" and convert to float
            image = item.get("image_url")

            new_product = Product(
                name=name,
                product_details_link=product_details_link,
                price=price,
                availability=True,
                location_latitude=None,
                location_longitude=None,
                image=image,
                vendor_name="Default Vendor",
                category_id=None,
                is_featured=False,
                is_popular=False,
                brand_id=None,
                camera_type_id=None,
                lens_type_id=None
            )

            db.session.add(new_product)

        db.session.commit()
    return jsonify({"message": "Products inserted successfully!"}), 201

@products_bp.route('/update_product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), 400

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

@products_bp.route('/delete/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to delete product", "error": str(e)}), 500

@products_bp.route("/products_list", methods=['GET'])
def get_products():
    products = Product.query.all()
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
    return jsonify(products_list), 200

@products_bp.route('/search_products', methods=['GET'])
def search_products():
    query = Product.query
    name = request.args.get('name')

    if name:
        query = query.filter(Product.name.ilike(f'%{name}%'))

    products = query.all()
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
    return jsonify(products_list), 200

@products_bp.route('/product/<int:product_id>', methods=['GET'])
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

@products_bp.route('/popular_products', methods=['GET'])
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

@products_bp.route('/featured_products', methods=['GET'])
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

@products_bp.route('/products/brand/<int:brand_id>', methods=['GET'])
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

@products_bp.route('/products/camera_type/<int:camera_type_id>', methods=['GET'])
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

@products_bp.route('/products/lens_type/<int:lens_type_id>', methods=['GET'])
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

@products_bp.route('/products/filtration', methods=['GET'])
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


# Additional routes such as get_product_details, popular_products, featured_products,
# get_products_by_brand, get_products_by_camera_type, get_products_by_lens_type,
# get_products_filtration can be added similarly.
