from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models.student import Student
from app.models.fee import Fee, Payment
from app.middlewares.auth import student_required

student_fee_bp = Blueprint('student_fee', __name__)

@student_fee_bp.route('/fees', methods=['GET'])
@student_required
def get_fees():
    """Get dormitory fees overview for student"""
    current_user_id = get_jwt_identity()
    student = Student.query.get(current_user_id)
    
    if not student or not student.current_dorm_id:
        return jsonify({'error': 'No dormitory assigned'}), 404
    
    # Get all fees for the student's dormitory
    fees = Fee.query.filter_by(dorm_id=student.current_dorm_id).order_by(Fee.created_at.desc()).all()
    
    # Calculate statistics
    total_fees = len(fees)
    paid_fees = sum(1 for f in fees if f.status == 'paid')
    unpaid_fees = sum(1 for f in fees if f.status == 'unpaid')
    total_amount = sum(float(f.amount) for f in fees)
    paid_amount = sum(float(f.amount) for f in fees if f.status == 'paid')
    unpaid_amount = sum(float(f.amount) for f in fees if f.status == 'unpaid')
    
    # Group fees by type
    fees_by_type = {}
    for fee in fees:
        fee_type = fee.fee_type or 'other'
        if fee_type not in fees_by_type:
            fees_by_type[fee_type] = []
        fees_by_type[fee_type].append({
            'fee_id': fee.fee_id,
            'fee_name': fee.fee_name or fee.fee_type,
            'maintenance_id': fee.maintenance_id,
            'amount': float(fee.amount),
            'status': fee.status,
            'created_at': fee.created_at.strftime('%Y-%m-%d %H:%M:%S') if fee.created_at else None,
            'initiated_by': fee.student_id  # 记录是谁发起的（如果是维修费用）
        })
    
    result = []
    for fee in fees:
        result.append({
            'fee_id': fee.fee_id,
            'dorm_id': fee.dorm_id,
            'fee_type': fee.fee_type,
            'fee_name': fee.fee_name or fee.fee_type,
            'maintenance_id': fee.maintenance_id,
            'amount': float(fee.amount),
            'status': fee.status,
            'created_at': fee.created_at.strftime('%Y-%m-%d %H:%M:%S') if fee.created_at else None,
            'initiated_by': fee.student_id
        })
    
    return jsonify({
        'fees': result,
        'statistics': {
            'total_fees': total_fees,
            'paid_fees': paid_fees,
            'unpaid_fees': unpaid_fees,
            'total_amount': round(total_amount, 2),
            'paid_amount': round(paid_amount, 2),
            'unpaid_amount': round(unpaid_amount, 2),
            'payment_rate': round((paid_fees / total_fees * 100) if total_fees > 0 else 0, 1)
        },
        'fees_by_type': fees_by_type
    }), 200

@student_fee_bp.route('/fees/<int:fee_id>/pay', methods=['POST'])
@student_required
def pay_fee(fee_id):
    """Pay dormitory fee - any student in the dormitory can pay"""
    current_user_id = get_jwt_identity()
    student = Student.query.get(current_user_id)
    
    if not student or not student.current_dorm_id:
        return jsonify({'error': 'No dormitory assigned'}), 404
    
    # Get fee - must belong to the student's dormitory
    fee = Fee.query.filter_by(fee_id=fee_id, dorm_id=student.current_dorm_id).first()
    
    if not fee:
        return jsonify({'error': 'Fee not found or you do not have permission to pay this fee'}), 404
    
    if fee.status == 'paid':
        return jsonify({'error': 'Fee already paid'}), 400
    
    data = request.get_json() or {}
    payment_method = data.get('payment_method', 'Online Payment')
    
    # Create payment record (any student in the dormitory can pay)
    payment = Payment(
        fee_id=fee_id,
        student_id=current_user_id,  # 记录是谁支付的
        amount=fee.amount,
        payment_method=payment_method
    )
    
    # Update fee status
    fee.status = 'paid'
    
    db.session.add(payment)
    db.session.commit()
    
    return jsonify({
        'message': 'Payment successful',
        'payment_id': payment.payment_id
    }), 200


