from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.student import Student
from app.middlewares.auth import student_required

student_profile_bp = Blueprint('student_profile', __name__)

@student_profile_bp.route('/profile', methods=['GET'])
@student_required
def get_profile():
    """Get student profile"""
    current_user_id = get_jwt_identity()
    student = Student.query.get(current_user_id)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    return jsonify({
        'student_id': student.student_id,
        'name': student.name,
        'email': student.email,
        'phone': student.phone,
        'gender': student.gender,
        'major': student.major
    }), 200

@student_profile_bp.route('/profile', methods=['PUT'])
@student_required
def update_profile():
    """Update student profile"""
    current_user_id = get_jwt_identity()
    student = Student.query.get(current_user_id)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    data = request.get_json()
    
    # Only allow updating phone
    if 'phone' in data:
        student.phone = data['phone']
    
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200


