from app import db

class Student(db.Model):
    """Student model"""
    __tablename__ = 'students'
    
    student_id = db.Column(db.String(20), db.ForeignKey('users.user_id'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Password field
    gender = db.Column(db.String(10), nullable=False)  # 'Male' or 'Female'
    major = db.Column(db.String(100), nullable=False)
    dormitory = db.Column(db.String(50), nullable=False)  # Building number
    room_number = db.Column(db.String(10), nullable=False)
    current_dorm_id = db.Column(db.String(20), db.ForeignKey('dormitories.dorm_id'))
    
    # Relationships
    user = db.relationship('User', backref='student', uselist=False)
    dormitory_obj = db.relationship('Dormitory', foreign_keys=[current_dorm_id], backref='students')
    
    def to_dict(self):
        return {
            'student_id': self.student_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'gender': self.gender,
            'major': self.major,
            'dormitory': self.dormitory,
            'room_number': self.room_number
        }


