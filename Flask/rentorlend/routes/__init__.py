# routes/__init__.py

from .brands import brands_bp
from .camera import camera_bp
from .enquiry import enquiry_bp
from .home_page import home_page_bp
from .lens import lens_bp
from .product_category import product_category_bp
from .products import products_bp
from .user import user_bp

# List of all blueprints to be registered in app.py
__all__ = [
    "brands_bp",
    "camera_bp",
    "enquiry_bp",
    "home_page_bp",
    "lens_bp",
    "product_category_bp",
    "products_bp",
    "user_bp"
]
