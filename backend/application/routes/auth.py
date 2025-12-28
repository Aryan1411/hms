from flask import Blueprint, request, jsonify
from application.models import User, Patient, Doctor
from application.database import db
from datetime import datetime, timedelta
import  jwt

import os

auth_bp = Blueprint('auth', __name__)


SECRET_KEY = os.environ.get('SECRET_KEY', 'This_is_my_secret')
JWT_EXPIRATION_HOURS = 24

def generate_token(user_id, role):
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        if user.is_blacklisted:
            return jsonify({'message': 'Account is blacklisted'}), 403
        
        if not user.active:
            return jsonify({'message': 'Account is inactive'}), 403
            
        # Generate JWT token
        token = generate_token(user.id, user.role)
        
        response_data = {
            'message': 'Login successful',
            'token': token,
            'role': user.role,
            'user_id': user.id
        }
        
        # Add role-specific IDs
        if user.role == 'doctor':
            doctor = Doctor.query.filter_by(user_id=user.id).first()
            if doctor:
                response_data['doctor_id'] = doctor.id
        elif user.role == 'patient':
            patient = Patient.query.filter_by(user_id=user.id).first()
            if patient:
                response_data['patient_id'] = patient.id
                
        return jsonify(response_data), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400
        
    new_user = User(username=username, role='patient', email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    # Create Patient profile
    new_patient = Patient(user_id=new_user.id, name=username)
    db.session.add(new_patient)
    db.session.commit()
    
    return jsonify({'message': 'Registration successful'}), 201

@auth_bp.route('/verify', methods=['GET'])
def verify():
    """Verify token endpoint"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'message': 'No token provided'}), 401
    
    try:
        token = auth_header.split(' ')[1]  # Bearer <token>
        payload = verify_token(token)
        if payload:
            return jsonify({'valid': True, 'user_id': payload['user_id'], 'role': payload['role']}), 200
        else:
            return jsonify({'valid': False, 'message': 'Invalid or expired token'}), 401
    except:
        return jsonify({'valid': False, 'message': 'Invalid token format'}), 401
