from datetime import datetime
from app import db

class MaintenanceType(db.Model):
    """Maintenance type model"""
    __tablename__ = 'maintenance_types'
    
    type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_name = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relationships
    maintenance_requests = db.relationship('MaintenanceRequest', backref='maintenance_type', lazy=True)
    
    def to_dict(self):
        return {
            'type_id': self.type_id,
            'type_name': self.type_name,
            'cost': float(self.cost)
        }

class MaintenanceRequest(db.Model):
    """Maintenance request model"""
    __tablename__ = 'maintenance_requests'
    
    maintenance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(20), db.ForeignKey('students.student_id'), nullable=False)
    dorm_id = db.Column(db.String(20), db.ForeignKey('dormitories.dorm_id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('maintenance_types.type_id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending/approved/rejected/completed
    processed_by = db.Column(db.String(20), db.ForeignKey('admins.admin_id'))
    processed_date = db.Column(db.DateTime)
    
    # Relationships
    student = db.relationship('Student', backref='maintenance_requests')
    dormitory = db.relationship('Dormitory', backref='maintenance_requests')
    
    def to_dict(self):
        return {
            'maintenance_id': self.maintenance_id,
            'student_id': self.student_id,
            'dorm_id': self.dorm_id,
            'type_id': self.type_id,
            'description': self.description,
            'request_date': self.request_date.isoformat() if self.request_date else None,
            'status': self.status,
            'processed_by': self.processed_by,
            'processed_date': self.processed_date.isoformat() if self.processed_date else None
        }



