from flask import Blueprint, request, jsonify
from app import db
from app.models.student import Student
from app.models.dormitory import Dormitory
from app.middlewares.auth import admin_required

admin_student_bp = Blueprint('admin_student', __name__)

@admin_student_bp.route('/students/unassigned', methods=['GET'])
@admin_required
def get_unassigned_students():
    """Get students without dormitory assignment"""
    students = Student.query.filter(
        (Student.current_dorm_id == None) | (Student.current_dorm_id == '')
    ).all()
    
    result = []
    for student in students:
        result.append({
            'student_id': student.student_id,
            'name': student.name,
            'email': student.email,
            'phone': student.phone,
            'gender': student.gender,
            'major': student.major,
            'dormitory': student.dormitory or 'Not assigned',
            'room_number': student.room_number or 'Not assigned'
        })
    
    return jsonify(result), 200

@admin_student_bp.route('/students/<student_id>/assign-dorm', methods=['POST'])
@admin_required
def assign_dormitory_to_student(student_id):
    """Assign dormitory to a student"""
    student = Student.query.get(student_id)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('dorm_id'):
        return jsonify({'error': 'Dormitory ID is required'}), 400
    
    dorm_id = data.get('dorm_id')
    
    # Check if dormitory exists
    dormitory = Dormitory.query.get(dorm_id)
    if not dormitory:
        return jsonify({'error': 'Dormitory not found'}), 404
    
    # Check if dormitory has vacancy
    if not dormitory.has_vacancy or dormitory.current_occupancy >= dormitory.max_capacity:
        return jsonify({'error': 'Selected dormitory is full'}), 400
    
    # Check gender match
    if student.gender != dormitory.gender:
        return jsonify({'error': f'Gender mismatch: Student is {student.gender}, but dormitory is for {dormitory.gender}'}), 400
    
    # If student already has a dormitory, remove from old one (only if different)
    if student.current_dorm_id and student.current_dorm_id != dorm_id:
        old_dorm = Dormitory.query.get(student.current_dorm_id)
        if old_dorm:
            old_dorm.current_occupancy = max(0, old_dorm.current_occupancy - 1)
            old_dorm.update_vacancy()
    
    # Only update occupancy if assigning to a different dormitory
    if not student.current_dorm_id or student.current_dorm_id != dorm_id:
        # Assign new dormitory
        student.current_dorm_id = dorm_id
        student.dormitory = f"Building {dormitory.building_id}"
        student.room_number = dormitory.room_no
        
        # Update dormitory occupancy
        dormitory.current_occupancy += 1
        dormitory.update_vacancy()
    else:
        # Student already in this dormitory, just update info if needed
        student.dormitory = f"Building {dormitory.building_id}"
        student.room_number = dormitory.room_no
    
    db.session.commit()
    
    return jsonify({
        'message': 'Dormitory assigned successfully',
        'student_id': student_id,
        'dorm_id': dorm_id
    }), 200

