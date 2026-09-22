from flask import Blueprint, jsonify, request
from app import db
from app.models.dormitory import Dormitory
from app.models.fee import Fee
from app.middlewares.auth import admin_required

admin_dorm_bp = Blueprint('admin_dorm', __name__)

@admin_dorm_bp.route('/dormitories', methods=['GET'])
@admin_required
def get_dormitory_status():
    """Get all dormitory status with payment information"""
    dormitories = Dormitory.query.all()
    
    result = []
    for dorm in dormitories:
        # Calculate payment statistics for students in this dormitory
        total_fees = 0
        paid_fees = 0
        unpaid_fees = 0
        total_amount = 0.0
        paid_amount = 0.0
        unpaid_amount = 0.0
        
        # Get all fees for this dormitory (not per student)
        dorm_fees = Fee.query.filter_by(dorm_id=dorm.dorm_id).all()
        for fee in dorm_fees:
            total_fees += 1
            total_amount += float(fee.amount)
            if fee.status == 'paid':
                paid_fees += 1
                paid_amount += float(fee.amount)
            else:
                unpaid_fees += 1
                unpaid_amount += float(fee.amount)
        
        # Calculate payment rate
        payment_rate = (paid_fees / total_fees * 100) if total_fees > 0 else 0
        
        result.append({
            'dorm_id': dorm.dorm_id,
            'building_id': dorm.building_id,
            'building_name': dorm.building.building_name if dorm.building else None,
            'floor_no': dorm.floor_no,
            'room_no': dorm.room_no,
            'gender': dorm.gender,
            'current_occupancy': dorm.current_occupancy,
            'max_capacity': dorm.max_capacity,
            'vacant_beds': dorm.vacant_beds,
            'has_vacancy': dorm.vacant_beds,  # 显示剩余床数而不是布尔值
            'payment_info': {
                'total_fees': total_fees,
                'paid_fees': paid_fees,
                'unpaid_fees': unpaid_fees,
                'total_amount': round(total_amount, 2),
                'paid_amount': round(paid_amount, 2),
                'unpaid_amount': round(unpaid_amount, 2),
                'payment_rate': round(payment_rate, 1)
            }
        })
    
    return jsonify(result), 200

@admin_dorm_bp.route('/dormitories/<dorm_id>/fees', methods=['POST'])
@admin_required
def create_dormitory_fee(dorm_id):
    """Create utility fee for a dormitory (e.g., water, electricity, internet)"""
    dormitory = Dormitory.query.get(dorm_id)
    
    if not dormitory:
        return jsonify({'error': 'Dormitory not found'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('fee_type') or not data.get('fee_name') or not data.get('amount'):
        return jsonify({'error': 'fee_type, fee_name, and amount are required'}), 400
    
    fee_type = data.get('fee_type')  # utilities, maintenance, etc.
    fee_name = data.get('fee_name')  # e.g., "Water & Electricity - January 2025"
    amount = float(data.get('amount'))
    
    if amount <= 0:
        return jsonify({'error': 'Amount must be greater than 0'}), 400
    
    # Create fee
    fee = Fee(
        dorm_id=dorm_id,
        student_id=None,  # Utility fees are not initiated by students
        maintenance_id=None,
        fee_type=fee_type,
        fee_name=fee_name,
        amount=amount,
        status='unpaid'
    )
    
    db.session.add(fee)
    db.session.commit()
    
    return jsonify({
        'message': 'Fee created successfully',
        'fee_id': fee.fee_id
    }), 201


