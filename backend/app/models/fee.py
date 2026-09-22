from datetime import datetime
from app import db

class Fee(db.Model):
    """Fee model - fees are associated with dormitories, not individual students"""
    __tablename__ = 'fees'
    
    fee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dorm_id = db.Column(db.String(20), db.ForeignKey('dormitories.dorm_id'), nullable=False)  # 费用关联到宿舍
    student_id = db.Column(db.String(20), db.ForeignKey('students.student_id'), nullable=True)  # 发起人（可选，用于维修费用）
    maintenance_id = db.Column(db.Integer, db.ForeignKey('maintenance_requests.maintenance_id'))  # 关联的维修请求（如果有）
    fee_type = db.Column(db.String(50), nullable=False, default='maintenance')  # 费用类型: maintenance, utilities, etc.
    fee_name = db.Column(db.String(100))  # 费用名称（如：水电费、网络费等）
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='unpaid')  # unpaid/paid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    dormitory = db.relationship('Dormitory', backref='fees')
    student = db.relationship('Student', backref='fees')  # 发起人
    maintenance_request = db.relationship('MaintenanceRequest', backref='fee')
    payments = db.relationship('Payment', backref='fee', lazy=True)
    
    def to_dict(self):
        return {
            'fee_id': self.fee_id,
            'dorm_id': self.dorm_id,
            'student_id': self.student_id,
            'maintenance_id': self.maintenance_id,
            'fee_type': self.fee_type,
            'fee_name': self.fee_name,
            'amount': float(self.amount),
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Payment(db.Model):
    """Payment model"""
    __tablename__ = 'payments'
    
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fee_id = db.Column(db.Integer, db.ForeignKey('fees.fee_id'), nullable=False)
    student_id = db.Column(db.String(20), db.ForeignKey('students.student_id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50), nullable=False)
    
    # Relationships
    student = db.relationship('Student', backref='payments')
    
    def to_dict(self):
        return {
            'payment_id': self.payment_id,
            'fee_id': self.fee_id,
            'student_id': self.student_id,
            'amount': float(self.amount),
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method
        }


