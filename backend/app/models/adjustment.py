from datetime import datetime
from app import db

class AdjustmentRequest(db.Model):
    """Adjustment request model"""
    __tablename__ = 'adjustment_requests'
    
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(20), db.ForeignKey('students.student_id'), nullable=False)
    current_dorm_id = db.Column(db.String(20), db.ForeignKey('dormitories.dorm_id'), nullable=False)
    request_reason = db.Column(db.Text, nullable=False)
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending/approved/rejected/cancelled
    processed_by = db.Column(db.String(20), db.ForeignKey('admins.admin_id'))
    processed_date = db.Column(db.DateTime)
    
    # Relationships
    student = db.relationship('Student', backref='adjustment_requests')
    current_dorm = db.relationship('Dormitory', foreign_keys=[current_dorm_id], backref='adjustment_requests')
    
    def to_dict(self):
        return {
            'request_id': self.request_id,
            'student_id': self.student_id,
            'current_dorm_id': self.current_dorm_id,
            'request_reason': self.request_reason,
            'request_date': self.request_date.isoformat() if self.request_date else None,
            'status': self.status,
            'processed_by': self.processed_by,
            'processed_date': self.processed_date.isoformat() if self.processed_date else None
        }



