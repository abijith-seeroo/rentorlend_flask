from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy instance
db = SQLAlchemy()

# Define the User model
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

# Define the ProductCategory model
class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_date = db.Column(db.DateTime, onupdate=db.func.current_timestamp())

# Define the Product model
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

# Define the Enquiry model
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

# Define the Brand model
class Brand(db.Model):
    __tablename__ = 'brand'
    brand_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_date = db.Column(db.DateTime, onupdate=db.func.current_timestamp())

# Define the CameraType model
class CameraType(db.Model):
    __tablename__ = 'camera_type'
    camera_type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_date = db.Column(db.DateTime, onupdate=db.func.current_timestamp())

# Define the LensType model
class LensType(db.Model):
    __tablename__ = 'lens_type'
    lens_type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_date = db.Column(db.DateTime, onupdate=db.func.current_timestamp())
