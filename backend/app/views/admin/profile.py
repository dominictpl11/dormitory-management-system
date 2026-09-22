from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.admin import Admin
from app.middlewares.auth import admin_required

admin_profile_bp = Blueprint('admin_profile', __name__)

@admin_profile_bp.route('/profile', methods=['GET'])
@admin_required
def get_admin_profile():
    """Get admin profile"""
    current_user_id = get_jwt_identity()
    admin = Admin.query.get(current_user_id)
    
    if not admin:
        return jsonify({'error': 'Admin not found'}), 404
    
    return jsonify({
        'admin_id': admin.admin_id,
        'name': admin.name,
        'email': admin.email,
        'phone': admin.phone
    }), 200

@admin_profile_bp.route('/profile', methods=['PUT'])
@admin_required
def update_admin_profile():
    """Update admin profile"""
    current_user_id = get_jwt_identity()
    admin = Admin.query.get(current_user_id)
    
    if not admin:
        return jsonify({'error': 'Admin not found'}), 404
    
    data = request.get_json()
    
    # Only allow updating phone
    if 'phone' in data:
        admin.phone = data['phone']
    
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200



