from flask import Blueprint, request, jsonify
from app import db
from app.models.maintenance import MaintenanceType
from app.middlewares.auth import admin_required

admin_maintenance_type_bp = Blueprint('admin_maintenance_type', __name__)

@admin_maintenance_type_bp.route('/maintenance-types', methods=['GET'])
@admin_required
def get_maintenance_types():
    """Get all maintenance types"""
    types = MaintenanceType.query.all()
    
    result = [type_obj.to_dict() for type_obj in types]
    
    return jsonify(result), 200

@admin_maintenance_type_bp.route('/maintenance-types', methods=['POST'])
@admin_required
def create_maintenance_type():
    """Create maintenance type"""
    data = request.get_json()
    
    if not data or not data.get('type_name') or not data.get('cost'):
        return jsonify({'error': 'Type name and cost are required'}), 400
    
    maintenance_type = MaintenanceType(
        type_name=data.get('type_name'),
        cost=data.get('cost')
    )
    
    db.session.add(maintenance_type)
    db.session.commit()
    
    return jsonify({
        'message': 'Maintenance type created successfully',
        'type_id': maintenance_type.type_id
    }), 201

@admin_maintenance_type_bp.route('/maintenance-types/<int:type_id>', methods=['PUT'])
@admin_required
def update_maintenance_type(type_id):
    """Update maintenance type"""
    maintenance_type = MaintenanceType.query.get(type_id)
    
    if not maintenance_type:
        return jsonify({'error': 'Maintenance type not found'}), 404
    
    data = request.get_json()
    
    if 'type_name' in data:
        maintenance_type.type_name = data['type_name']
    if 'cost' in data:
        maintenance_type.cost = data['cost']
    
    db.session.commit()
    
    return jsonify({'message': 'Maintenance type updated successfully'}), 200

@admin_maintenance_type_bp.route('/maintenance-types/<int:type_id>', methods=['DELETE'])
@admin_required
def delete_maintenance_type(type_id):
    """Delete maintenance type"""
    maintenance_type = MaintenanceType.query.get(type_id)
    
    if not maintenance_type:
        return jsonify({'error': 'Maintenance type not found'}), 404
    
    db.session.delete(maintenance_type)
    db.session.commit()
    
    return jsonify({'message': 'Maintenance type deleted successfully'}), 200



