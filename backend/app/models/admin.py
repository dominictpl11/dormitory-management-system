from app import db

class Admin(db.Model):
    """Admin model"""
    __tablename__ = 'admins'
    
    admin_id = db.Column(db.String(20), db.ForeignKey('users.user_id'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Password field
    
    # Relationships
    user = db.relationship('User', backref='admin', uselist=False)
    
    def to_dict(self):
        return {
            'admin_id': self.admin_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone
        }


