"""Database initialization script"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import (
    User, Student, Admin, Building, Dormitory,
    MaintenanceType, MaintenanceRequest, AdjustmentRequest, Fee, Payment
)
from app.auth.utils import hash_password

def init_database():
    """Initialize database with tables and sample data"""
    app = create_app()
    
    with app.app_context():
        # Drop all tables (for development)
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Create admin users
        admins_data = [
            {'admin_id': 'admin1', 'name': 'Admin One', 'phone': '00000000001'},
            {'admin_id': 'admin2', 'name': 'Admin Two', 'phone': '00000000002'},
            {'admin_id': 'admin3', 'name': 'Admin Three', 'phone': '00000000003'}
        ]
        
        for admin_data in admins_data:
            admin_id = admin_data['admin_id']
            # Create user
            admin_user = User(
                user_id=admin_id,
                username=admin_id,
                password_hash=hash_password('123456'),
                email=f'{admin_id}@example.invalid',
                phone=admin_data['phone'],
                role='admin'
            )
            db.session.add(admin_user)
            
            # Create admin
            admin = Admin(
                admin_id=admin_id,
                name=admin_data['name'],
                email=f'{admin_id}@example.invalid',
                phone=admin_data['phone'],
                password_hash=admin_user.password_hash  # Copy password from user
            )
            db.session.add(admin)
        
        # Create buildings
        buildings_data = [
            {'building_id': 'A', 'building_name': 'Building A'},
            {'building_id': 'B', 'building_name': 'Building B'},
            {'building_id': 'C', 'building_name': 'Building C'},
            {'building_id': 'D', 'building_name': 'Building D'},
            {'building_id': 'E', 'building_name': 'Building E'}
        ]
        
        for building_data in buildings_data:
            building = Building(
                building_id=building_data['building_id'],
                building_name=building_data['building_name']
            )
            db.session.add(building)
        
        db.session.commit()
        
        # Create dormitories
        # AB栋为男生宿舍，CD栋为女生宿舍
        # Building A: 30 rooms (25 for first 100 students + 5 empty) - 男生
        # Building B: 25 rooms for 100 students - 男生
        # Building C: 25 rooms for 100 students - 女生
        # Building D: 25 rooms for 100 students - 女生
        dormitories_data = []
        
        # Building A: 30 rooms (25 filled + 5 empty) - 男生宿舍
        for floor in range(1, 7):  # 6 floors
            for room in range(1, 6):  # 5 rooms per floor
                room_no = f"{floor}{room:02d}"
                dorm_id = f"A-{room_no}"
                dormitories_data.append({
                    'dorm_id': dorm_id,
                    'building_id': 'A',
                    'floor_no': floor,
                    'room_no': room_no,
                    'gender': 'Male',
                    'max_capacity': 4
                })
        
        # Building B: 25 rooms - 男生宿舍
        for floor in range(1, 6):  # 5 floors
            for room in range(1, 6):  # 5 rooms per floor
                room_no = f"{floor}{room:02d}"
                dorm_id = f"B-{room_no}"
                dormitories_data.append({
                    'dorm_id': dorm_id,
                    'building_id': 'B',
                    'floor_no': floor,
                    'room_no': room_no,
                    'gender': 'Male',
                    'max_capacity': 4
                })
        
        # Building C: 30 rooms (25 filled + 5 empty) - 女生宿舍
        for floor in range(1, 7):  # 6 floors
            for room in range(1, 6):  # 5 rooms per floor
                room_no = f"{floor}{room:02d}"
                dorm_id = f"C-{room_no}"
                dormitories_data.append({
                    'dorm_id': dorm_id,
                    'building_id': 'C',
                    'floor_no': floor,
                    'room_no': room_no,
                    'gender': 'Female',
                    'max_capacity': 4
                })
        
        # Building D: 25 rooms - 女生宿舍
        for floor in range(1, 6):  # 5 floors
            for room in range(1, 6):  # 5 rooms per floor
                room_no = f"{floor}{room:02d}"
                dorm_id = f"D-{room_no}"
                dormitories_data.append({
                    'dorm_id': dorm_id,
                    'building_id': 'D',
                    'floor_no': floor,
                    'room_no': room_no,
                    'gender': 'Female',
                    'max_capacity': 4
                })
        
        for dorm_data in dormitories_data:
            dormitory = Dormitory(
                dorm_id=dorm_data['dorm_id'],
                building_id=dorm_data['building_id'],
                floor_no=dorm_data['floor_no'],
                room_no=dorm_data['room_no'],
                gender=dorm_data['gender'],
                max_capacity=dorm_data['max_capacity'],
                current_occupancy=0,
                vacant_beds=dorm_data['max_capacity'],  # 初始化剩余床位数
                has_vacancy=True
            )
            db.session.add(dormitory)
        
        db.session.commit()
        
        import random
        
        # 专业列表
        majors = [
            'Computer Science', 'Mathematics', 'Physics', 'Chemistry', 'Biology',
            'Economics', 'Finance', 'Business Administration', 'Accounting', 'Marketing',
            'Electrical Engineering', 'Mechanical Engineering', 'Civil Engineering', 'Chemical Engineering',
            'Psychology', 'Sociology', 'Political Science', 'International Relations', 'History', 'Literature'
        ]
        
        # Use neutral names so the seed data cannot be mistaken for a real roster.
        # Create 200 students (100 males for AB栋, 100 females for CD栋)
        # Building A: 25 rooms for 100 male students
        # Building B: 25 rooms for 100 male students (但实际上我们只分配100个男生到AB栋)
        # Building C: 25 rooms for 100 female students
        # Building D: 25 rooms for 100 female students (但实际上我们只分配100个女生到CD栋)
        
        # 分配100个男生到Building A (25 rooms, 每个房间4人)
        male_dormitories = Dormitory.query.filter(
            Dormitory.building_id == 'A',
            Dormitory.gender == 'Male'
        ).order_by(Dormitory.dorm_id).all()
        
        male_dorm_index = 0
        
        for i in range(100):
            student_id = f"{100000000 + i}"
            name = f"Sample Student {student_id}"
            phone = f"000{10000000 + i:08d}"
            gender = 'Male'
            major = random.choice(majors)
            
            dorm = male_dormitories[male_dorm_index]
            building_name = f"Building {dorm.building_id}"
            room_number = dorm.room_no
            
            # Create user
            student_user = User(
                user_id=student_id,
                username=student_id,
                password_hash=hash_password('123456'),
                email=f'{student_id}@example.invalid',
                phone=phone,
                role='student'
            )
            db.session.add(student_user)
            
            # Create student
            student = Student(
                student_id=student_id,
                name=name,
                email=f'{student_id}@example.invalid',
                phone=phone,
                password_hash=student_user.password_hash,  # Copy password from user
                gender=gender,
                major=major,
                dormitory=building_name,
                room_number=room_number,
                current_dorm_id=dorm.dorm_id
            )
            db.session.add(student)
            
            # Update dormitory occupancy
            dorm.current_occupancy += 1
            dorm.update_vacancy()
            
            # Move to next dormitory if current one is full (4 students)
            if dorm.current_occupancy >= dorm.max_capacity:
                male_dorm_index += 1
        
        db.session.commit()
        
        # 分配100个女生到Building C (25 rooms, 每个房间4人，留5个空宿舍)
        female_dormitories = Dormitory.query.filter(
            Dormitory.building_id == 'C',
            Dormitory.gender == 'Female'
        ).order_by(Dormitory.dorm_id).all()
        
        female_dorm_index = 0
        
        for i in range(100):
            student_id = f"{200000000 + i}"
            name = f"Sample Student {student_id}"
            phone = f"000{20000000 + i:08d}"
            gender = 'Female'
            major = random.choice(majors)
            
            # Use only first 25 dormitories (leave last 5 empty)
            dorm = female_dormitories[female_dorm_index]
            building_name = f"Building {dorm.building_id}"
            room_number = dorm.room_no
            
            # Create user
            student_user = User(
                user_id=student_id,
                username=student_id,
                password_hash=hash_password('123456'),
                email=f'{student_id}@example.invalid',
                phone=phone,
                role='student'
            )
            db.session.add(student_user)
            
            # Create student
            student = Student(
                student_id=student_id,
                name=name,
                email=f'{student_id}@example.invalid',
                phone=phone,
                password_hash=student_user.password_hash,  # Copy password from user
                gender=gender,
                major=major,
                dormitory=building_name,
                room_number=room_number,
                current_dorm_id=dorm.dorm_id
            )
            db.session.add(student)
            
            # Update dormitory occupancy
            dorm.current_occupancy += 1
            dorm.update_vacancy()
            
            # Move to next dormitory if current one is full (4 students)
            if dorm.current_occupancy >= dorm.max_capacity:
                female_dorm_index += 1
        
        db.session.commit()
        
        # 再分配100个男生到Building B (25 rooms, 每个房间4人)
        male_dormitories_b = Dormitory.query.filter(
            Dormitory.building_id == 'B',
            Dormitory.gender == 'Male'
        ).order_by(Dormitory.dorm_id).all()
        
        male_dorm_index_b = 0
        
        for i in range(100):
            student_id = f"{300000000 + i}"
            name = f"Sample Student {student_id}"
            phone = f"000{30000000 + i:08d}"
            gender = 'Male'
            major = random.choice(majors)
            
            dorm = male_dormitories_b[male_dorm_index_b]
            building_name = f"Building {dorm.building_id}"
            room_number = dorm.room_no
            
            # Create user
            student_user = User(
                user_id=student_id,
                username=student_id,
                password_hash=hash_password('123456'),
                email=f'{student_id}@example.invalid',
                phone=phone,
                role='student'
            )
            db.session.add(student_user)
            
            # Create student
            student = Student(
                student_id=student_id,
                name=name,
                email=f'{student_id}@example.invalid',
                phone=phone,
                password_hash=student_user.password_hash,  # Copy password from user
                gender=gender,
                major=major,
                dormitory=building_name,
                room_number=room_number,
                current_dorm_id=dorm.dorm_id
            )
            db.session.add(student)
            
            # Update dormitory occupancy
            dorm.current_occupancy += 1
            dorm.update_vacancy()
            
            # Move to next dormitory if current one is full (4 students)
            if dorm.current_occupancy >= dorm.max_capacity:
                male_dorm_index_b += 1
        
        db.session.commit()
        
        # 再分配100个女生到Building D (25 rooms, 每个房间4人)
        female_dormitories_d = Dormitory.query.filter(
            Dormitory.building_id == 'D',
            Dormitory.gender == 'Female'
        ).order_by(Dormitory.dorm_id).all()
        
        female_dorm_index_d = 0
        
        for i in range(100):
            student_id = f"{400000000 + i}"
            name = f"Sample Student {student_id}"
            phone = f"000{40000000 + i:08d}"
            gender = 'Female'
            major = random.choice(majors)
            
            dorm = female_dormitories_d[female_dorm_index_d]
            building_name = f"Building {dorm.building_id}"
            room_number = dorm.room_no
            
            # Create user
            student_user = User(
                user_id=student_id,
                username=student_id,
                password_hash=hash_password('123456'),
                email=f'{student_id}@example.invalid',
                phone=phone,
                role='student'
            )
            db.session.add(student_user)
            
            # Create student
            student = Student(
                student_id=student_id,
                name=name,
                email=f'{student_id}@example.invalid',
                phone=phone,
                password_hash=student_user.password_hash,  # Copy password from user
                gender=gender,
                major=major,
                dormitory=building_name,
                room_number=room_number,
                current_dorm_id=dorm.dorm_id
            )
            db.session.add(student)
            
            # Update dormitory occupancy
            dorm.current_occupancy += 1
            dorm.update_vacancy()
            
            # Move to next dormitory if current one is full (4 students)
            if dorm.current_occupancy >= dorm.max_capacity:
                female_dorm_index_d += 1
        
        db.session.commit()
        
        # Create maintenance types
        maintenance_types_data = [
            {'type_name': 'Faucet Repair', 'cost': 50.00},
            {'type_name': 'Light Fixture Repair', 'cost': 30.00},
            {'type_name': 'Air Conditioner Repair', 'cost': 200.00},
            {'type_name': 'Network Issue', 'cost': 20.00},
            {'type_name': 'Door Lock Repair', 'cost': 80.00}
        ]
        
        for type_data in maintenance_types_data:
            maintenance_type = MaintenanceType(
                type_name=type_data['type_name'],
                cost=type_data['cost']
            )
            db.session.add(maintenance_type)
        
        db.session.commit()
        
        print("Database initialized successfully!")
        print("\nPre-created accounts:")
        print("Admins: admin1/123456, admin2/123456, admin3/123456")
        print(f"Students: 400 students created")
        print("  - 200 Male students:")
        print("    * 100 students (IDs: 100000000-100000099) in Building A (Male)")
        print("    * 100 students (IDs: 300000000-300000099) in Building B (Male)")
        print("  - 200 Female students:")
        print("    * 100 students (IDs: 200000000-200000099) in Building C (Female)")
        print("    * 100 students (IDs: 400000000-400000099) in Building D (Female)")
        print("All students use password: 123456")
        print("\nDormitory allocation:")
        print("- Building A (Male): 30 dormitories (25 fully occupied, 5 empty)")
        print("- Building B (Male): 25 dormitories (all fully occupied)")
        print("- Building C (Female): 30 dormitories (25 fully occupied, 5 empty)")
        print("- Building D (Female): 25 dormitories (all fully occupied)")
        print("- Total: 110 dormitories created")
        print("\nGender-based dormitory assignment:")
        print("- Buildings A & B: Male dormitories")
        print("- Buildings C & D: Female dormitories")

if __name__ == '__main__':
    init_database()


