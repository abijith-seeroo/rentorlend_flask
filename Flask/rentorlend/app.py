from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from flasgger import Swagger
from models import db
from services import login, logout, token_required  # Import functions from services package
from routes import (
    brands_bp,
    camera_bp,
    enquiry_bp,
    home_page_bp,
    lens_bp,
    product_category_bp,
    products_bp,
    user_bp
)

app = Flask(__name__)




# Set configuration before initializing the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:new_password@localhost:5432/rental_database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'here_is_my_secret_key'

Swagger(app)

# Initialize the database with the app
db.init_app(app)



SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'  # Define the location of your JSON spec if using external documentation
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

app.register_blueprint(user_bp)
app.register_blueprint(products_bp)
app.register_blueprint(product_category_bp)
app.register_blueprint(brands_bp)
app.register_blueprint(camera_bp)
app.register_blueprint(lens_bp)
app.register_blueprint(home_page_bp)
app.register_blueprint(enquiry_bp)


# Register login route
@app.route('/login', methods=['POST', 'GET'])
def login_route():
    return login()

# Register logout route
@app.route('/logout', methods=['POST', 'GET'])
def logout_route():
    return logout()

@app.route('/protected', methods=['GET'])
@token_required
def protected_route(current_user):
    return jsonify({'message': f'Welcome {current_user.name}! This is a protected route.'})






@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


if __name__ == '__main__':
    # with app.app_context():
        # db.drop_all()
        # db.create_all()  # Creates all tables defined
    app.run(debug=True)