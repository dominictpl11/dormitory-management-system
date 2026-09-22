from app import db

class Building(db.Model):
    """Building model"""
    __tablename__ = 'buildings'
    
    building_id = db.Column(db.String(10), primary_key=True)
    building_name = db.Column(db.String(100), nullable=False)
    
    # Relationships
    dormitories = db.relationship('Dormitory', backref='building', lazy=True)
    
    def to_dict(self):
        return {
            'building_id': self.building_id,
            'building_name': self.building_name
        }

class Dormitory(db.Model):
    """Dormitory model"""
    __tablename__ = 'dormitories'
    
    dorm_id = db.Column(db.String(20), primary_key=True)  # Dormitory No.
    building_id = db.Column(db.String(10), db.ForeignKey('buildings.building_id'), nullable=False)  # Building No.
    floor_no = db.Column(db.Integer, nullable=False)  # Floor No.
    room_no = db.Column(db.String(10), nullable=False)  # Dormitory Door No.
    gender = db.Column(db.String(10), nullable=False)  # 'Male' or 'Female' - AB栋为男生，CD栋为女生
    max_capacity = db.Column(db.Integer, nullable=False, default=4)  # Count of Beds
    current_occupancy = db.Column(db.Integer, nullable=False, default=0)  # Current occupancy
    vacant_beds = db.Column(db.Integer, nullable=False, default=4)  # Count of Vacant bed (数据库字段)
    has_vacancy = db.Column(db.Boolean, nullable=False, default=True)
    
    def update_vacancy(self):
        """Update vacant_beds and has_vacancy based on current occupancy"""
        self.vacant_beds = max(0, self.max_capacity - self.current_occupancy)
        self.has_vacancy = self.vacant_beds > 0
    
    def to_dict(self):
        return {
            'dorm_id': self.dorm_id,
            'building_id': self.building_id,
            'floor_no': self.floor_no,
            'room_no': self.room_no,
            'gender': self.gender,
            'current_occupancy': self.current_occupancy,
            'max_capacity': self.max_capacity,
            'vacant_beds': self.vacant_beds,  # 数据库字段
            'has_vacancy': self.vacant_beds  # 显示剩余床数而不是布尔值
        }


