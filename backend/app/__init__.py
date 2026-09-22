import os
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import sys

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    """Application factory"""
    # Get the backend directory (parent of app directory)
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Frontend directory is sibling of backend directory
    frontend_dir = os.path.join(os.path.dirname(backend_dir), 'frontend')
    app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Enable CORS for all routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    from app.auth.routes import auth_bp
    from app.views.student.profile import student_profile_bp
    from app.views.student.dormitory import student_dorm_bp
    from app.views.student.adjustment import student_adjustment_bp
    from app.views.student.maintenance import student_maintenance_bp
    from app.views.student.fee import student_fee_bp
    from app.views.admin.profile import admin_profile_bp
    from app.views.admin.dormitory import admin_dorm_bp
    from app.views.admin.adjustment import admin_adjustment_bp
    from app.views.admin.maintenance import admin_maintenance_bp
    from app.views.admin.maintenance_type import admin_maintenance_type_bp
    from app.views.admin.student import admin_student_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(student_profile_bp, url_prefix='/api/student')
    app.register_blueprint(student_dorm_bp, url_prefix='/api/student')
    app.register_blueprint(student_adjustment_bp, url_prefix='/api/student')
    app.register_blueprint(student_maintenance_bp, url_prefix='/api/student')
    app.register_blueprint(student_fee_bp, url_prefix='/api/student')
    app.register_blueprint(admin_profile_bp, url_prefix='/api/admin')
    app.register_blueprint(admin_dorm_bp, url_prefix='/api/admin')
    app.register_blueprint(admin_adjustment_bp, url_prefix='/api/admin')
    app.register_blueprint(admin_maintenance_bp, url_prefix='/api/admin')
    app.register_blueprint(admin_maintenance_type_bp, url_prefix='/api/admin')
    app.register_blueprint(admin_student_bp, url_prefix='/api/admin')
    
    # Serve frontend files (must be after API routes)
    @app.route('/', defaults={'path': 'index.html'})
    @app.route('/<path:path>')
    def serve_static(path):
        # Don't serve API routes as static files
        if path.startswith('api/'):
            from flask import abort
            abort(404)
        
        # Serve index.html for root
        if path == '' or path == '/':
            path = 'index.html'
        
        try:
            return send_from_directory(app.static_folder, path)
        except Exception as e:
            # If file not found and it's an HTML request, serve index.html (for SPA routing)
            if not '.' in path or path.endswith('.html'):
                return send_from_directory(app.static_folder, 'index.html')
            raise e
    
    return app

