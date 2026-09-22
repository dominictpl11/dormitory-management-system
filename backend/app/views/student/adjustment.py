from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models.student import Student
from app.models.adjustment import AdjustmentRequest
from app.middlewares.auth import student_required

student_adjustment_bp = Blueprint('student_adjustment', __name__)

@student_adjustment_bp.route('/adjustments', methods=['POST'])
@student_required
def create_adjustment_request():
    """Create adjustment request"""
    current_user_id = get_jwt_identity()
    student = Student.query.get(current_user_id)
    
    if not student or not student.current_dorm_id:
        return jsonify({'error': 'No dormitory assigned, cannot submit adjustment request'}), 400
    
    data = request.get_json()
    
    if not data or not data.get('request_reason'):
        return jsonify({'error': 'Request reason is required'}), 400
    
    # Create adjustment request
    adjustment_request = AdjustmentRequest(
        student_id=current_user_id,
        current_dorm_id=student.current_dorm_id,
        request_reason=data.get('request_reason'),
        status='pending'
    )
    
    db.session.add(adjustment_request)
    db.session.commit()
    
    return jsonify({
        'message': 'Adjustment request submitted successfully',
        'request_id': adjustment_request.request_id
    }), 201

@student_adjustment_bp.route('/adjustments', methods=['GET'])
@student_required
def get_adjustment_requests():
    """Get student adjustment requests"""
    current_user_id = get_jwt_identity()
    
    requests = AdjustmentRequest.query.filter_by(
        student_id=current_user_id
    ).order_by(AdjustmentRequest.request_date.desc()).all()
    
    result = []
    for req in requests:
        result.append({
            'request_id': req.request_id,
            'request_reason': req.request_reason,
            'status': req.status,
            'request_date': req.request_date.strftime('%Y-%m-%d %H:%M:%S') if req.request_date else None,
            'processed_date': req.processed_date.strftime('%Y-%m-%d %H:%M:%S') if req.processed_date else None
        })
    
    return jsonify(result), 200

@student_adjustment_bp.route('/adjustments/<int:request_id>', methods=['DELETE'])
@student_required
def cancel_adjustment_request(request_id):
    """Cancel adjustment request"""
    current_user_id = get_jwt_identity()
    
    adjustment_request = AdjustmentRequest.query.filter_by(
        request_id=request_id,
        student_id=current_user_id
    ).first()
    
    if not adjustment_request:
        return jsonify({'error': 'Adjustment request not found'}), 404
    
    if adjustment_request.status != 'pending':
        return jsonify({'error': 'Only pending requests can be cancelled'}), 400
    
    adjustment_request.status = 'cancelled'
    db.session.commit()
    
    return jsonify({'message': 'Adjustment request cancelled successfully'}), 200



