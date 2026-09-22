from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models.maintenance import MaintenanceRequest
from app.models.student import Student
from app.models.dormitory import Dormitory
from app.models.fee import Fee
from app.middlewares.auth import admin_required

admin_maintenance_bp = Blueprint('admin_maintenance', __name__)

@admin_maintenance_bp.route('/maintenances', methods=['GET'])
@admin_required
def get_all_maintenance_requests():
    """Get all maintenance requests"""
    status = request.args.get('status')
    
    query = MaintenanceRequest.query
    
    if status:
        query = query.filter_by(status=status)
    
    requests = query.order_by(MaintenanceRequest.request_date.desc()).all()
    
    result = []
    for req in requests:
        student = Student.query.get(req.student_id)
        dormitory = Dormitory.query.get(req.dorm_id)
        result.append({
            'maintenance_id': req.maintenance_id,
            'student_id': req.student_id,
            'student_name': student.name if student else 'Unknown',
            'dorm_id': req.dorm_id,
            'building_id': dormitory.building_id if dormitory else None,
            'room_no': dormitory.room_no if dormitory else None,
            'type_id': req.type_id,
            'type_name': req.maintenance_type.type_name if req.maintenance_type else None,
            'description': req.description,
            'status': req.status,
            'request_date': req.request_date.strftime('%Y-%m-%d %H:%M:%S') if req.request_date else None,
            'processed_date': req.processed_date.strftime('%Y-%m-%d %H:%M:%S') if req.processed_date else None
        })
    
    return jsonify(result), 200

@admin_maintenance_bp.route('/maintenances/<int:maintenance_id>', methods=['PUT'])
@admin_required
def process_maintenance_request(maintenance_id):
    """Process maintenance request"""
    current_user_id = get_jwt_identity()
    
    maintenance = MaintenanceRequest.query.get(maintenance_id)
    
    if not maintenance:
        return jsonify({'error': 'Maintenance request not found'}), 404
    
    data = request.get_json()
    
    if not data or data.get('status') not in ['approved', 'rejected', 'completed']:
        return jsonify({'error': 'Invalid status, must be approved, rejected, or completed'}), 400
    
    old_status = maintenance.status
    maintenance.status = data.get('status')
    maintenance.processed_by = current_user_id
    maintenance.processed_date = datetime.utcnow()
    
    # If approved, create fee (associated with dormitory, not individual student)
    if data.get('status') == 'approved' and old_status != 'approved':
        if maintenance.maintenance_type:
            fee = Fee(
                dorm_id=maintenance.dorm_id,  # 费用关联到宿舍
                student_id=maintenance.student_id,  # 记录发起人
                maintenance_id=maintenance_id,
                fee_type='maintenance',
                fee_name=f"Maintenance: {maintenance.maintenance_type.type_name}",
                amount=maintenance.maintenance_type.cost,
                status='unpaid'
            )
            db.session.add(fee)
    
    db.session.commit()
    
    return jsonify({'message': 'Maintenance request processed successfully'}), 200


