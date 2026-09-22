from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models.user import User
from app.models.student import Student
from app.auth.utils import hash_password, verify_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400
    
    user = User.query.filter_by(username=data.get('username')).first()
    
    if not user or not verify_password(user.password_hash, data.get('password')):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Update last login time
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create access token
    access_token = create_access_token(
        identity=user.user_id,
        additional_claims={'role': user.role}
    )
    
    return jsonify({
        'access_token': access_token,
        'role': user.role,
        'user_id': user.user_id
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    """Student registration"""
    data = request.get_json()
    
    # Validate required fields
    if not data:
        return jsonify({'error': 'Registration data is required'}), 400
    
    required_fields = ['student_id', 'password', 'name', 'email', 'phone', 'gender', 'major']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    student_id = data.get('student_id')
    # Username automatically uses student_id
    username = data.get('username', student_id)
    password = data.get('password')
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    gender = data.get('gender')
    major = data.get('major')
    
    # Validate gender
    if gender not in ['Male', 'Female']:
        return jsonify({'error': 'Gender must be Male or Female'}), 400
    
    # Check if student_id already exists
    if User.query.filter_by(user_id=student_id).first():
        return jsonify({'error': 'Student ID already exists'}), 400
    
    # Check if username (student_id) already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Student ID already exists'}), 400
    
    # Check if email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    try:
        # Create user
        user = User(
            user_id=student_id,
            username=username,
            password_hash=hash_password(password),
            email=email,
            phone=phone,
            role='student'
        )
        db.session.add(user)
        
        # Create student (without dormitory assignment initially)
        student = Student(
            student_id=student_id,
            name=name,
            email=email,
            phone=phone,
            password_hash=user.password_hash,  # Copy password from user
            gender=gender,
            major=major,
            dormitory='',  # Will be assigned later
            room_number='',  # Will be assigned later
            current_dorm_id=None
        )
        db.session.add(student)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Registration successful',
            'student_id': student_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change password"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('old_password') or not data.get('new_password'):
        return jsonify({'error': 'Old password and new password are required'}), 400
    
    # Verify old password
    if not verify_password(user.password_hash, data.get('old_password')):
        return jsonify({'error': 'Invalid old password'}), 400
    
    # Set new password
    new_password_hash = hash_password(data.get('new_password'))
    user.password_hash = new_password_hash
    
    # Also update password in student or admin table
    if user.role == 'student':
        from app.models.student import Student
        student = Student.query.get(user.user_id)
        if student:
            student.password_hash = new_password_hash
    elif user.role == 'admin':
        from app.models.admin import Admin
        admin = Admin.query.get(user.user_id)
        if admin:
            admin.password_hash = new_password_hash
    
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200


