from flask import Blueprint, jsonify, request
from application.models import Doctor, User, Patient, Appointment, Availability, Treatment
from application.database import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    doctors = Doctor.query.filter(Doctor.name.contains(query) | Doctor.department.contains(query)).all()
    patients = Patient.query.filter(Patient.name.contains(query)).all()
    
    return jsonify({
        'doctors': [{'id': d.id, 'name': d.name, 'department': d.department} for d in doctors],
        'patients': [{'id': p.id, 'name': p.name} for p in patients]
    })

@admin_bp.route('/blacklist/<int:user_id>', methods=['PUT'])
def toggle_blacklist(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blacklisted = not user.is_blacklisted
    db.session.commit()
    status = 'blacklisted' if user.is_blacklisted else 'active'
    return jsonify({'message': f'User {status}'}), 200

@admin_bp.route('/doctors', methods=['GET', 'POST'])
def manage_doctors():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        name = data.get('name')
        specialization = data.get('specialization')
        department = data.get('department')
        
        if User.query.filter_by(username=username).first():
            return jsonify({'message': 'Username exists'}), 400
            
        user = User(username=username, role='doctor')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        doctor = Doctor(user_id=user.id, name=name, specialization=specialization, department=department)
        db.session.add(doctor)
        db.session.commit()
        return jsonify({'message': 'Doctor added'}), 201
        
    doctors = Doctor.query.all()
    return jsonify([{
        'id': d.id, 
        'name': d.name, 
        'specialization': d.specialization,
        'department': d.department,
        'user_id': d.user_id,
        'is_blacklisted': d.user.is_blacklisted
    } for d in doctors])

@admin_bp.route('/doctors/<int:id>', methods=['PUT'])
def update_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    data = request.get_json()
    doctor.name = data.get('name', doctor.name)
    doctor.specialization = data.get('specialization', doctor.specialization)
    doctor.department = data.get('department', doctor.department)
    db.session.commit()
    return jsonify({'message': 'Doctor updated'}), 200

@admin_bp.route('/doctors/<int:id>', methods=['DELETE'])
def delete_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    user = User.query.get(doctor.user_id)
    
    # Delete all appointments and their treatments for this doctor
    appointments = Appointment.query.filter_by(doctor_id=id).all()
    for appointment in appointments:
        if appointment.treatment:
            db.session.delete(appointment.treatment)
        db.session.delete(appointment)
    
    # Delete all availability slots
    availabilities = Availability.query.filter_by(doctor_id=id).all()
    for avail in availabilities:
        db.session.delete(avail)
    
    db.session.delete(doctor)
    if user:
        db.session.delete(user)
    
    db.session.commit()
    return jsonify({'message': 'Doctor deleted successfully'}), 200

@admin_bp.route('/patients', methods=['GET', 'POST'])
def manage_patients():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        dob = data.get('dob')
        contact = data.get('contact')
        
        if User.query.filter_by(username=username).first():
            return jsonify({'message': 'Username already exists'}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already exists'}), 400
            
        user = User(username=username, email=email, role='patient')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        patient = Patient(user_id=user.id, name=name, contact=contact)
        if dob:
            from datetime import datetime
            patient.dob = datetime.strptime(dob, '%Y-%m-%d').date()
        db.session.add(patient)
        db.session.commit()
        return jsonify({'message': 'Patient added'}), 201
        
    patients = Patient.query.all()
    return jsonify([{
        'id': p.id, 
        'name': p.name,
        'dob': str(p.dob) if p.dob else None,
        'contact': p.contact,
        'user_id': p.user_id,
        'is_blacklisted': p.user.is_blacklisted
    } for p in patients])

@admin_bp.route('/patients/<int:id>', methods=['PUT'])
def update_patient(id):
    patient = Patient.query.get_or_404(id)
    data = request.get_json()
    patient.name = data.get('name', patient.name)
    patient.contact = data.get('contact', patient.contact)
    if data.get('dob'):
        from datetime import datetime
        patient.dob = datetime.strptime(data.get('dob'), '%Y-%m-%d').date()
    db.session.commit()
    return jsonify({'message': 'Patient updated'}), 200

@admin_bp.route('/patients/<int:id>', methods=['DELETE'])
def delete_patient(id):
    patient = Patient.query.get_or_404(id)
    user = User.query.get(patient.user_id)
    
    # Delete all appointments and their treatments for this patient
    appointments = Appointment.query.filter_by(patient_id=id).all()
    for appointment in appointments:
        if appointment.treatment:
            db.session.delete(appointment.treatment)
        db.session.delete(appointment)
    
    db.session.delete(patient)
    if user:
        db.session.delete(user)
    
    db.session.commit()
    return jsonify({'message': 'Patient deleted successfully'}), 200

@admin_bp.route('/appointments', methods=['GET'])
def get_appointments():
    appointments = Appointment.query.all()
    return jsonify([{
        'id': a.id, 
        'doctor': a.doctor.name, 
        'patient': a.patient.name, 
        'date': str(a.date), 
        'time': str(a.time),
        'status': a.status,
        'reason': a.reason or 'Not specified'
    } for a in appointments])

@admin_bp.route('/appointments/<int:id>/cancel', methods=['PUT'])
def cancel_appointment_admin(id):
    appointment = Appointment.query.get_or_404(id)
    appointment.status = 'Cancelled'
    db.session.commit()
    return jsonify({'message': 'Appointment cancelled'}), 200
