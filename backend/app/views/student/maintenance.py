from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.student import Student
from app.models.maintenance import MaintenanceRequest, MaintenanceType
from app.middlewares.auth import student_required

student_maintenance_bp = Blueprint('student_maintenance', __name__)

@student_maintenance_bp.route('/maintenance-types', methods=['GET'])
@student_required
def get_maintenance_types():
    """Get all maintenance types (for students to select when submitting requests)"""
    types = MaintenanceType.query.all()
    
    result = [type_obj.to_dict() for type_obj in types]
    
    return jsonify(result), 200

@student_maintenance_bp.route('/maintenances', methods=['POST'])
@student_required
def create_maintenance_request():
    """Create maintenance request"""
    current_user_id = get_jwt_identity()
    student = Student.query.get(current_user_id)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    if not student.current_dorm_id:
        return jsonify({'error': 'No dormitory assigned, cannot submit maintenance request'}), 400
    
    data = request.get_json()
    
    if not data or not data.get('type_id') or not data.get('description'):
        return jsonify({'error': 'Type ID and description are required'}), 400
    
    # Create maintenance request
    maintenance = MaintenanceRequest(
        student_id=current_user_id,
        dorm_id=student.current_dorm_id,
        type_id=data.get('type_id'),
        description=data.get('description'),
        status='pending'
    )
    
    db.session.add(maintenance)
    db.session.commit()
    
    return jsonify({
        'message': 'Maintenance request submitted successfully',
        'maintenance_id': maintenance.maintenance_id
    }), 201

@student_maintenance_bp.route('/maintenances', methods=['GET'])
@student_required
def get_maintenance_requests():
    """Get student maintenance requests"""
    current_user_id = get_jwt_identity()
    
    requests = MaintenanceRequest.query.filter_by(
        student_id=current_user_id
    ).order_by(MaintenanceRequest.request_date.desc()).all()
    
    result = []
    for req in requests:
        result.append({
            'maintenance_id': req.maintenance_id,
            'type_id': req.type_id,
            'type_name': req.maintenance_type.type_name if req.maintenance_type else None,
            'description': req.description,
            'status': req.status,
            'request_date': req.request_date.strftime('%Y-%m-%d %H:%M:%S') if req.request_date else None,
            'processed_date': req.processed_date.strftime('%Y-%m-%d %H:%M:%S') if req.processed_date else None
        })
    
    return jsonify(result), 200

@student_maintenance_bp.route('/maintenances/<int:maintenance_id>', methods=['PUT'])
@student_required
def update_maintenance_request(maintenance_id):
    """Update maintenance request (only pending ones)"""
    current_user_id = get_jwt_identity()
    
    maintenance = MaintenanceRequest.query.filter_by(
        maintenance_id=maintenance_id,
        student_id=current_user_id
    ).first()
    
    if not maintenance:
        return jsonify({'error': 'Maintenance request not found'}), 404
    
    if maintenance.status != 'pending':
        return jsonify({'error': 'Only pending requests can be updated'}), 400
    
    data = request.get_json()
    
    if 'description' in data:
        maintenance.description = data['description']
    if 'type_id' in data:
        maintenance.type_id = data['type_id']
    
    db.session.commit()
    
    return jsonify({'message': 'Maintenance request updated successfully'}), 200

@student_maintenance_bp.route('/maintenances/<int:maintenance_id>', methods=['DELETE'])
@student_required
def cancel_maintenance_request(maintenance_id):
    """Cancel maintenance request"""
    current_user_id = get_jwt_identity()
    
    maintenance = MaintenanceRequest.query.filter_by(
        maintenance_id=maintenance_id,
        student_id=current_user_id
    ).first()
    
    if not maintenance:
        return jsonify({'error': 'Maintenance request not found'}), 404
    
    if maintenance.status != 'pending':
        return jsonify({'error': 'Only pending requests can be cancelled'}), 400
    
    maintenance.status = 'cancelled'
    db.session.commit()
    
    return jsonify({'message': 'Maintenance request cancelled successfully'}), 200


