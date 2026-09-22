from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models.adjustment import AdjustmentRequest
from app.models.student import Student
from app.models.dormitory import Dormitory
from app.middlewares.auth import admin_required

admin_adjustment_bp = Blueprint('admin_adjustment', __name__)

@admin_adjustment_bp.route('/adjustments/available-dorms', methods=['GET'])
@admin_required
def get_available_dormitories():
    """Get available dormitories for adjustment"""
    # Get current dorm ID and student ID from query parameters
    exclude_dorm_id = request.args.get('exclude_dorm_id')
    student_id = request.args.get('student_id')
    
    # Get student gender if student_id is provided
    student_gender = None
    if student_id:
        student = Student.query.get(student_id)
        if student:
            student_gender = student.gender
    
    query = Dormitory.query.filter(
        Dormitory.has_vacancy == True,
        Dormitory.current_occupancy < Dormitory.max_capacity
    )
    
    # Filter by gender if student gender is known
    if student_gender:
        query = query.filter(Dormitory.gender == student_gender)
    
    # Exclude current dormitory if provided
    if exclude_dorm_id:
        query = query.filter(Dormitory.dorm_id != exclude_dorm_id)
    
    dormitories = query.order_by(Dormitory.building_id, Dormitory.room_no).all()
    
    result = []
    for dorm in dormitories:
            result.append({
                'dorm_id': dorm.dorm_id,
                'building_id': dorm.building_id,
                'building_name': dorm.building.building_name if dorm.building else None,
                'floor_no': dorm.floor_no,
                'room_no': dorm.room_no,
                'gender': dorm.gender,
                'current_occupancy': dorm.current_occupancy,
                'max_capacity': dorm.max_capacity,
                'available_spots': dorm.vacant_beds,
                'has_vacancy': dorm.vacant_beds  # 显示剩余床数而不是布尔值
            })
    
    return jsonify(result), 200

@admin_adjustment_bp.route('/adjustments', methods=['GET'])
@admin_required
def get_all_adjustment_requests():
    """Get all adjustment requests"""
    status = request.args.get('status')
    
    query = AdjustmentRequest.query
    
    if status:
        query = query.filter_by(status=status)
    
    requests = query.order_by(AdjustmentRequest.request_date.desc()).all()
    
    result = []
    for req in requests:
        student = Student.query.get(req.student_id)
        current_dorm = Dormitory.query.get(req.current_dorm_id) if req.current_dorm_id else None
        result.append({
            'request_id': req.request_id,
            'student_id': req.student_id,
            'student_name': student.name if student else 'Unknown',
            'current_dorm_id': req.current_dorm_id,
            'current_dorm': f"{current_dorm.building_id}-{current_dorm.room_no}" if current_dorm else 'N/A',
            'student_gender': student.gender if student else None,
            'request_reason': req.request_reason,
            'status': req.status,
            'request_date': req.request_date.strftime('%Y-%m-%d %H:%M:%S') if req.request_date else None,
            'processed_date': req.processed_date.strftime('%Y-%m-%d %H:%M:%S') if req.processed_date else None
        })
    
    return jsonify(result), 200

@admin_adjustment_bp.route('/adjustments/<int:request_id>', methods=['PUT'])
@admin_required
def process_adjustment_request(request_id):
    """Process adjustment request"""
    current_user_id = get_jwt_identity()
    
    adjustment_request = AdjustmentRequest.query.get(request_id)
    
    if not adjustment_request:
        return jsonify({'error': 'Adjustment request not found'}), 404
    
    data = request.get_json()
    
    if not data or data.get('status') not in ['approved', 'rejected']:
        return jsonify({'error': 'Invalid status, must be approved or rejected'}), 400
    
    student = Student.query.get(adjustment_request.student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # If approved, assign new dormitory
    if data.get('status') == 'approved':
        new_dorm_id = data.get('new_dorm_id')
        if not new_dorm_id:
            return jsonify({'error': 'New dormitory ID is required for approval'}), 400
        
        # Check if new dormitory exists
        new_dorm = Dormitory.query.get(new_dorm_id)
        if not new_dorm:
            return jsonify({'error': 'New dormitory not found'}), 404
        
        # Check if new dormitory has vacancy
        if not new_dorm.has_vacancy or new_dorm.current_occupancy >= new_dorm.max_capacity:
            return jsonify({'error': 'Selected dormitory is full'}), 400
        
        # Check gender match
        if student.gender != new_dorm.gender:
            return jsonify({'error': f'Gender mismatch: Student is {student.gender}, but dormitory is for {new_dorm.gender}'}), 400
        
        # Get old dormitory
        old_dorm = student.dormitory_obj
        
        # Only update if moving to a different dormitory
        if not old_dorm or old_dorm.dorm_id != new_dorm_id:
            # Update old dormitory occupancy (decrease) - only if different
            if old_dorm and old_dorm.dorm_id != new_dorm_id:
                old_dorm.current_occupancy = max(0, old_dorm.current_occupancy - 1)
                old_dorm.update_vacancy()
            
            # Update student dormitory assignment
            student.current_dorm_id = new_dorm_id
            student.dormitory = f"Building {new_dorm.building_id}"
            student.room_number = new_dorm.room_no
            
            # Update new dormitory occupancy (increase) - only if different
            if not old_dorm or old_dorm.dorm_id != new_dorm_id:
                new_dorm.current_occupancy += 1
                new_dorm.update_vacancy()
        else:
            # Student already in this dormitory, just update info if needed
            student.dormitory = f"Building {new_dorm.building_id}"
            student.room_number = new_dorm.room_no
    
    # Update request status
    adjustment_request.status = data.get('status')
    adjustment_request.processed_by = current_user_id
    adjustment_request.processed_date = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Adjustment request processed successfully'}), 200


