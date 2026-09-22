from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.student import Student
from app.models.dormitory import Dormitory
from app.middlewares.auth import student_required

student_dorm_bp = Blueprint('student_dorm', __name__)

@student_dorm_bp.route('/dormitory', methods=['GET'])
@student_required
def get_dormitory_info():
    """Get student dormitory information"""
    current_user_id = get_jwt_identity()
    student = Student.query.get(current_user_id)
    
    if not student or not student.current_dorm_id:
        return jsonify({'error': 'No dormitory assigned'}), 404
    
    # Get dormitory information
    dormitory = Dormitory.query.get(student.current_dorm_id)
    if not dormitory:
        return jsonify({'error': 'Dormitory not found'}), 404
    
    # Get roommates
    roommates = Student.query.filter(
        Student.current_dorm_id == student.current_dorm_id,
        Student.student_id != current_user_id
    ).all()
    
    roommate_names = [roommate.name for roommate in roommates]
    
    return jsonify({
        'dorm_building': dormitory.building_id,
        'room_number': dormitory.room_no,
        'roommates': roommate_names
    }), 200



