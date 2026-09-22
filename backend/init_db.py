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
            {'admin_id': 'admin1', 'name': 'Admin One', 'phone': '13800000001'},
            {'admin_id': 'admin2', 'name': 'Admin Two', 'phone': '13800000002'},
            {'admin_id': 'admin3', 'name': 'Admin Three', 'phone': '13800000003'}
        ]
        
        for admin_data in admins_data:
            admin_id = admin_data['admin_id']
            # Create user
            admin_user = User(
                user_id=admin_id,
                username=admin_id,
                password_hash=hash_password('123456'),
                email=f'{admin_id}@cuhk.edu.cn',
                phone=admin_data['phone'],
                role='admin'
            )
            db.session.add(admin_user)
            
            # Create admin
            admin = Admin(
                admin_id=admin_id,
                name=admin_data['name'],
                email=f'{admin_id}@cuhk.edu.cn',
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
        
        # 生成200个男生名字（用于AB栋）
        male_names = [
            'James Smith', 'Robert Williams', 'Michael Jones', 'William Miller', 'David Moore',
            'Richard Anderson', 'Joseph Jackson', 'Thomas Harris', 'Christopher Thompson', 'Charles Martinez',
            'Daniel Clark', 'Matthew Lewis', 'Anthony Walker', 'Mark Allen', 'Donald King',
            'Steven Lopez', 'Paul Scott', 'Andrew Adams', 'Kenneth Gonzalez', 'Joshua Carter',
            'Kevin Roberts', 'Brian Phillips', 'George Parker', 'Edward Edwards', 'Ronald Stewart',
            'Timothy Morris', 'Jason Reed', 'Jeffrey Morgan', 'Ryan Murphy', 'Jacob Rivera',
            'Gary Richardson', 'Nicholas Howard', 'Eric Torres', 'Jonathan Gray', 'Stephen James',
            'Larry Brooks', 'Justin Sanders', 'Scott Bennett', 'Brandon Barnes', 'Benjamin Henderson',
            'Samuel Jenkins', 'Frank Powell', 'Raymond Patterson', 'Alexander Flores', 'Patrick Butler',
            'Jack Foster', 'Dennis Bryant', 'Jerry Russell', 'Peter Johnson', 'Henry Wilson',
            'Nathan Brooks', 'Connor Murphy', 'Ethan White', 'Mason Harris', 'Noah Davis',
            'Lucas Brown', 'Aiden Miller', 'Carter Taylor', 'Logan Williams', 'Jackson Davis',
            'Owen Wilson', 'Wyatt Lewis', 'Henry Hall', 'Leo Young', 'Miles Lopez',
            'Julian Green', 'Eli Baker', 'Caleb Nelson', 'Grayson Mitchell', 'Landon Turner',
            'Adrian Campbell', 'Zachary Evans', 'Isaac Collins', 'Levi Sanchez', 'Aaron Rogers',
            'Evan Cook', 'Axel Bell', 'Ian Bailey', 'Jaxon Cooper', 'Colton Cox',
            'Bentley Ward', 'Easton Peterson', 'Cooper Ramirez', 'Parker Watson', 'Nolan Kelly',
            'Tristan Price', 'Declan Wood', 'Silas Ross', 'Jasper Coleman', 'Ryder Perry',
            'Bennett Long', 'Kai Hughes', 'Maxwell Washington', 'Theodore Simmons', 'Asher Gonzales',
            'Dominic Alexander', 'Xavier Griffin', 'Jace Hayes', 'Brayden Ford', 'Kayden Graham',
            'Blake Wallace', 'Lincoln Cole', 'Elias Brooks', 'Roman Owens', 'Greyson Fisher',
            'Oliver Stone', 'Gabriel Knight', 'Felix Sterling', 'Caspian Wave', 'Orion Bright',
            'Atlas Strong', 'River Stone', 'Mountain Peak', 'Valley Deep', 'Crystal Clear',
            'Diamond Sparkle', 'Pearl Shine', 'Silver Light', 'Gold Rush', 'Bronze Medal',
            'Copper Wire', 'Platinum Edge', 'Titanium Steel', 'Cobalt Blue', 'Mercury Silver',
            'Jupiter King', 'Mars Warrior', 'Saturn Ring', 'Neptune Ocean', 'Venus Star',
            'Apollo Sun', 'Zeus Thunder', 'Poseidon Wave', 'Hades Shadow', 'Ares Battle',
            'Hermes Speed', 'Dionysus Wine', 'Hephaestus Fire', 'Athena Wisdom', 'Artemis Moon',
            'Aphrodite Love', 'Demeter Earth', 'Hestia Hearth', 'Persephone Spring', 'Hera Queen',
            'Loki Trick', 'Thor Hammer', 'Odin Allfather', 'Freya Beauty', 'Tyr Justice',
            'Baldur Bright', 'Heimdall Watch', 'Frigg Queen', 'Sif Golden', 'Idun Youth',
            'Fenrir Wolf', 'Jormungandr Serpent', 'Hel Death', 'Valkyrie Warrior', 'Einherjar Hero',
            'Ragnar Lothbrok', 'Bjorn Ironside', 'Ivar Boneless', 'Sigurd Snake', 'Harald Fairhair',
            'Rollo Viking', 'Leif Erikson', 'Erik Red', 'Canute Great', 'Sweyn Forkbeard',
            'William Conqueror', 'Richard Lionheart', 'Edward Longshanks', 'Henry Tudor', 'Charles Stuart',
            'James Stuart', 'George Hanover', 'Edward Windsor', 'Albert Saxe', 'Louis Bourbon',
            'Philip Habsburg', 'Ferdinand Aragon', 'Isabella Castile', 'Francis Valois', 'Henry Valois',
            'Charles Valois', 'Louis Capet', 'Philip Capet', 'Robert Capet', 'Hugh Capet',
            'Otto Saxon', 'Henry Saxon', 'Conrad Salian', 'Henry Salian', 'Frederick Hohenstaufen',
            'Rudolf Habsburg', 'Albert Habsburg', 'Leopold Habsburg', 'Maximilian Habsburg', 'Charles Habsburg',
            'Philip Habsburg', 'Ferdinand Habsburg', 'Matthias Habsburg', 'Rudolf Habsburg', 'Joseph Habsburg',
            'Francis Habsburg', 'Ferdinand Habsburg', 'Franz Joseph', 'Charles Habsburg', 'Otto Habsburg'
        ]
        
        # 生成200个女生名字（用于CD栋）
        female_names = [
            'Mary Johnson', 'Patricia Brown', 'Jennifer Davis', 'Linda Wilson', 'Elizabeth Taylor',
            'Barbara Thomas', 'Susan White', 'Jessica Martin', 'Sarah Garcia', 'Karen Robinson',
            'Nancy Rodriguez', 'Betty Lee', 'Margaret Hall', 'Sandra Young', 'Donna Wright',
            'Carol Hill', 'Ruth Green', 'Sharon Baker', 'Michelle Nelson', 'Laura Mitchell',
            'Emily Turner', 'Kimberly Campbell', 'Deborah Evans', 'Amanda Collins', 'Melissa Sanchez',
            'Stephanie Rogers', 'Rebecca Cook', 'Sharon Bell', 'Cynthia Bailey', 'Kathleen Cooper',
            'Amy Cox', 'Angela Ward', 'Brenda Peterson', 'Emma Ramirez', 'Rachel Watson',
            'Carolyn Kelly', 'Janet Price', 'Maria Wood', 'Heather Ross', 'Diane Coleman',
            'Lisa Perry', 'Michelle Long', 'Emily Hughes', 'Debra Washington', 'Kimberly Simmons',
            'Donna Gonzales', 'Carol Alexander', 'Anna Martinez', 'Olivia Davis', 'Sophia Brown',
            'Victoria Taylor', 'Grace Mitchell', 'Chloe Martinez', 'Zoe Thompson', 'Ava Jackson',
            'Isabella Wilson', 'Mia Garcia', 'Charlotte Moore', 'Amelia Johnson', 'Harper Jones',
            'Evelyn Martinez', 'Abigail Rodriguez', 'Emily Clark', 'Madison Walker', 'Sofia Allen',
            'Avery King', 'Luna Wright', 'Scarlett Hill', 'Aria Adams', 'Layla Gonzalez',
            'Nora Carter', 'Riley Roberts', 'Hannah Phillips', 'Addison Parker', 'Aubrey Edwards',
            'Ellie Stewart', 'Natalie Morris', 'Savannah Reed', 'Brooklyn Morgan', 'Leah Murphy',
            'Stella Rivera', 'Hazel Richardson', 'Violet Howard', 'Aurora Torres', 'Willow Gray',
            'Claire James', 'Skylar Brooks', 'Lucy Sanders', 'Paisley Bennett', 'Naomi Barnes',
            'Elena Henderson', 'Maya Jenkins', 'Aaliyah Powell', 'Lillian Patterson', 'Ariana Flores',
            'Kinsley Butler', 'Katherine Foster', 'Liliana Bryant', 'Nevaeh Russell', 'Bella Diaz',
            'Arianna Myers', 'Mackenzie Hamilton', 'Samantha Sullivan', 'Allison Woods', 'Genesis West',
            'Alyssa Jordan', 'Eva Reynolds', 'Caroline Ellis', 'Kylie Gibson', 'Autumn Reeves',
            'Piper Burns', 'Lyla Shaw', 'Natalia Tucker', 'Faith Hunter', 'Alexis Crawford',
            'Isabelle Boyd', 'Ruby Morales', 'Sophie Watts', 'Lillian Schultz', 'Ariana Bishop',
            'Kinsley Mullins', 'Katherine Hodges', 'Liliana Berger', 'Nevaeh Frank', 'Bella Harrington',
            'Penelope Chase', 'Isla Moon', 'Violet Rose', 'Hazel Bloom', 'Phoenix Star',
            'Ivy Lane', 'Seraphina Sky', 'Luna Star', 'Aurora Dawn', 'Willow Tree',
            'Ocean Blue', 'Forest Green', 'Sapphire Blue', 'Emerald Green', 'Ruby Red',
            'Amethyst Purple', 'Topaz Yellow', 'Tanzanite Blue', 'Alexandrite Color', 'Moonstone White',
            'Peridot Green', 'Citrine Yellow', 'Jade Green', 'Turquoise Blue', 'Coral Pink',
            'Rose Petal', 'Lily Bloom', 'Daisy Field', 'Tulip Spring', 'Orchid Beauty',
            'Jasmine Night', 'Lavender Dream', 'Iris Color', 'Sunflower Bright', 'Cherry Blossom',
            'Magnolia White', 'Peony Pink', 'Carnation Red', 'Marigold Gold', 'Zinnia Rainbow',
            'Poppy Red', 'Daffodil Yellow', 'Hyacinth Blue', 'Gardenia White', 'Camellia Pink',
            'Azalea Spring', 'Rhododendron Mountain', 'Wisteria Purple', 'Clematis Climb', 'Honeysuckle Sweet',
            'Jasmine Tea', 'Lilac Purple', 'Forsythia Yellow', 'Dogwood White', 'Redbud Pink',
            'Crabapple Red', 'Hawthorn White', 'Elderberry Dark', 'Serviceberry Blue', 'Chokecherry Red',
            'Sage Green', 'Thyme Herb', 'Rosemary Leaf', 'Basil Fresh', 'Mint Cool',
            'Oregano Spice', 'Parsley Green', 'Cilantro Fresh', 'Dill Weed', 'Chive Onion',
            'Tarragon Fine', 'Marjoram Sweet', 'Bay Leaf', 'Fennel Seed', 'Anise Star',
            'Cardamom Pod', 'Cinnamon Stick', 'Nutmeg Spice', 'Clove Bud', 'Vanilla Bean',
            'Ginger Root', 'Turmeric Gold', 'Saffron Thread', 'Paprika Red', 'Cumin Seed',
            'Coriander Seed', 'Mustard Yellow', 'Peppercorn Black', 'Star Anise', 'Fenugreek Seed',
            'Sumac Berry', 'Zaatar Mix', 'Harissa Hot', 'Berbere Spice', 'Ras El Hanout',
            'Baharat Mix', 'Dukkah Nut', 'Tajin Season', 'Old Bay', 'Cajun Spice',
            'Jerk Season', 'Adobo Mix', 'Garam Masala', 'Curry Powder', 'Tandoori Mix',
            'Garam Spice', 'Panch Phoron', 'Chaat Masala', 'Sambar Powder', 'Rasam Mix',
            'Biryani Spice', 'Korma Mix', 'Vindaloo Hot', 'Tikka Masala', 'Butter Chicken',
            'Tandoori Chicken', 'Chicken Curry', 'Lamb Curry', 'Beef Curry', 'Fish Curry',
            'Vegetable Curry', 'Dal Tadka', 'Chana Masala', 'Aloo Gobi', 'Palak Paneer',
            'Baingan Bharta', 'Mutter Paneer', 'Navratan Korma', 'Malai Kofta', 'Shahi Paneer'
        ]
        
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
            name = male_names[i] if i < len(male_names) else f"Male Student {i}"
            phone = f"139{str(10000000 + i).zfill(8)}"
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
                email=f'{student_id}@link.cuhk.edu.cn',
                phone=phone,
                role='student'
            )
            db.session.add(student_user)
            
            # Create student
            student = Student(
                student_id=student_id,
                name=name,
                email=f'{student_id}@link.cuhk.edu.cn',
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
            name = female_names[i] if i < len(female_names) else f"Female Student {i}"
            phone = f"139{str(20000000 + i).zfill(8)}"
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
                email=f'{student_id}@link.cuhk.edu.cn',
                phone=phone,
                role='student'
            )
            db.session.add(student_user)
            
            # Create student
            student = Student(
                student_id=student_id,
                name=name,
                email=f'{student_id}@link.cuhk.edu.cn',
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
            name = male_names[100 + i] if (100 + i) < len(male_names) else f"Male Student {100 + i}"
            phone = f"139{str(30000000 + i).zfill(8)}"
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
                email=f'{student_id}@link.cuhk.edu.cn',
                phone=phone,
                role='student'
            )
            db.session.add(student_user)
            
            # Create student
            student = Student(
                student_id=student_id,
                name=name,
                email=f'{student_id}@link.cuhk.edu.cn',
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
            name = female_names[100 + i] if (100 + i) < len(female_names) else f"Female Student {100 + i}"
            phone = f"139{str(40000000 + i).zfill(8)}"
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
                email=f'{student_id}@link.cuhk.edu.cn',
                phone=phone,
                role='student'
            )
            db.session.add(student_user)
            
            # Create student
            student = Student(
                student_id=student_id,
                name=name,
                email=f'{student_id}@link.cuhk.edu.cn',
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


