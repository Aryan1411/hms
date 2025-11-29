from flask import Blueprint, jsonify, request
from application.models import Doctor, Appointment, Availability, Patient, User
from application.database import db
from datetime import datetime

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/departments', methods=['GET'])
def get_departments():
    
    doctors = Doctor.query.with_entities(Doctor.department).distinct().all()
    departments = [d.department for d in doctors if d.department]
    return jsonify(departments)

@patient_bp.route('/search', methods=['GET'])
def search_doctors():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    
    doctors = Doctor.query.filter(
        (Doctor.name.ilike(f'%{query}%')) | 
        (Doctor.department.ilike(f'%{query}%')) |
        (Doctor.specialization.ilike(f'%{query}%'))
    ).all()
    
    return jsonify([{
        'id': d.id, 
        'name': d.name, 
        'specialization': d.specialization,
        'department': d.department
    } for d in doctors])

@patient_bp.route('/department/<string:department>/doctors', methods=['GET'])
def get_doctors_by_department(department):
    doctors = Doctor.query.filter_by(department=department).all()
    return jsonify([{'id': d.id, 'name': d.name, 'specialization': d.specialization} for d in doctors])

@patient_bp.route('/doctor/<int:doctor_id>/availability', methods=['GET'])
def get_doctor_availability(doctor_id):
    
    slots = Availability.query.filter_by(doctor_id=doctor_id).all()
    return jsonify([{
        'id': s.id, 
        'date': str(s.date), 
        'start_time': str(s.start_time), 
        'end_time': str(s.end_time),
        'is_booked': s.is_booked
    } for s in slots])

@patient_bp.route('/book_slot', methods=['POST'])
def book_slot():
    data = request.get_json()
    slot_id = data.get('slot_id')
    patient_id = data.get('patient_id')
    reason = data.get('reason', '')
    
    slot = Availability.query.get_or_404(slot_id)
    if slot.is_booked:
        return jsonify({'message': 'Slot already booked'}), 400
        
    slot.is_booked = True
    
    appointment = Appointment(
        doctor_id=slot.doctor_id, 
        patient_id=patient_id, 
        date=slot.date, 
        time=slot.start_time,
        reason=reason
    )
    db.session.add(appointment)
    db.session.commit()
    
    return jsonify({'message': 'Appointment booked successfully'}), 201

@patient_bp.route('/doctors', methods=['GET'])
def get_doctors():
    doctors = Doctor.query.all()
    return jsonify([{'id': d.id, 'name': d.name, 'specialization': d.specialization} for d in doctors])

@patient_bp.route('/book', methods=['POST'])
def book_appointment():
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    patient_id = data.get('patient_id') 
    date_str = data.get('date')
    time_str = data.get('time')
    
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    time_obj = datetime.strptime(time_str, '%H:%M').time()
    
    appointment = Appointment(doctor_id=doctor_id, patient_id=patient_id, date=date_obj, time=time_obj)
    db.session.add(appointment)
    db.session.commit()
    
    return jsonify({'message': 'Appointment booked'}), 201

@patient_bp.route('/appointments/<int:patient_id>', methods=['GET'])
def get_appointments(patient_id):
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.date.desc()).all()
    return jsonify([{
        'id': a.id, 
        'doctor': a.doctor.name, 
        'specialization': a.doctor.specialization,
        'date': str(a.date), 
        'time': str(a.time), 
        'status': a.status
    } for a in appointments])

@patient_bp.route('/appointments/<int:id>/cancel', methods=['PUT'])
def cancel_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    
    
    avail = Availability.query.filter_by(
        doctor_id=appointment.doctor_id,
        date=appointment.date,
        start_time=appointment.time,
        is_booked=True
    ).first()
    
    if avail:
        avail.is_booked = False
        
    appointment.status = 'Cancelled'
    db.session.commit()
    return jsonify({'message': 'Appointment cancelled and slot freed'}), 200

@patient_bp.route('/history/<int:patient_id>', methods=['GET'])
def get_history(patient_id):
    
    appointments = Appointment.query.filter_by(patient_id=patient_id, status='Completed').all()
    history = []
    for app in appointments:
        if app.treatment:
            history.append({
                'date': str(app.date),
                'doctor': app.doctor.name,
                'diagnosis': app.treatment.diagnosis,
                'prescription': app.treatment.prescription
            })
    return jsonify(history)


@patient_bp.route('/export-treatments/<int:patient_id>', methods=['POST'])
def trigger_export(patient_id):
    """Trigger async CSV export job"""
    from application.tasks import export_patient_treatments
    
    
    task = export_patient_treatments.delay(patient_id)
    
    return jsonify({
        'message': 'Export started',
        'task_id': task.id
    }), 202

@patient_bp.route('/export-status/<task_id>', methods=['GET'])
def check_export_status(task_id):
    from application.tasks import export_patient_treatments
    from celery.result import AsyncResult
    
    task = AsyncResult(task_id, app=export_patient_treatments.app)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'result': task.result
        }
    elif task.state == 'FAILURE':
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    else:
        response = {
            'state': task.state,
            'status': 'Processing...'
        }
    
    return jsonify(response)

@patient_bp.route('/download-export/<filename>', methods=['GET'])
def download_export(filename):
    """Download exported CSV file"""
    from flask import send_from_directory
    import application.config as config
    import os
    
    import sys
    
    sys.stderr.write(f"=== DOWNLOAD REQUEST ===\n")
    sys.stderr.write(f"Requested filename: {filename}\n")
    sys.stderr.write(f"EXPORT_FOLDER: {config.EXPORT_FOLDER}\n")
    
    filepath = os.path.join(config.EXPORT_FOLDER, filename)
    sys.stderr.write(f"Full filepath: {filepath}\n")
    sys.stderr.write(f"File exists: {os.path.exists(filepath)}\n")
    
    if os.path.exists(config.EXPORT_FOLDER):
        sys.stderr.write(f"Files in export folder:\n")
        files = os.listdir(config.EXPORT_FOLDER)
        for f in files:
            sys.stderr.write(f"  - {f}\n")
    else:
        sys.stderr.write(f"Export folder does not exist!\n")
    
    sys.stderr.write(f"========================\n")
    sys.stderr.flush()
    
    if not os.path.exists(filepath):
        return jsonify({'message': 'File not found', 'debug_path': filepath}), 404
    
    return send_from_directory(config.EXPORT_FOLDER, filename, as_attachment=True)
    
    if not os.path.exists(filepath):
        return jsonify({'message': 'File not found'}), 404
    
    return send_from_directory(config.EXPORT_FOLDER, filename, as_attachment=True)
def manage_profile(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': patient.id,
            'name': patient.name,
            'dob': str(patient.dob) if patient.dob else None,
            'contact': patient.contact,
            'email': patient.user.email
        })
    
    elif request.method == 'PUT':
        data = request.get_json()
        patient.name = data.get('name', patient.name)
        if data.get('dob'):
            patient.dob = datetime.strptime(data.get('dob'), '%Y-%m-%d').date()
        patient.contact = data.get('contact', patient.contact)
        
        # Update user email if provided
        if data.get('email'):
            patient.user.email = data.get('email')
        
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200

@patient_bp.route('/appointments/<int:appointment_id>/reschedule', methods=['PUT'])
def reschedule_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    data = request.get_json()
    
    new_date_str = data.get('date')
    new_time_str = data.get('time')
    
    if new_date_str:
        appointment.date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
    if new_time_str:
        appointment.time = datetime.strptime(new_time_str, '%H:%M').time()
    
    db.session.commit()
    return jsonify({'message': 'Appointment rescheduled successfully'}), 200

@patient_bp.route('/profile/<int:patient_id>', methods=['GET'])
def get_patient_profile(patient_id):
    """Get patient profile information"""
    patient = Patient.query.get_or_404(patient_id)
    user = User.query.get(patient.user_id)
    
    return jsonify({
        'name': patient.name,
        'dob': str(patient.dob) if patient.dob else '',
        'contact': patient.contact or '',
        'email': user.email if user else ''
    })

@patient_bp.route('/profile/<int:patient_id>', methods=['PUT'])
def update_patient_profile(patient_id):
    """Update patient profile information"""
    data = request.get_json()
    
    patient = Patient.query.get_or_404(patient_id)
    user = User.query.get(patient.user_id)
    
    # Update patient fields
    if 'name' in data:
        patient.name = data['name']
    if 'dob' in data and data['dob']:
        try:
            patient.dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
        except:
            pass
    if 'contact' in data:
        patient.contact = data['contact']
    
    # Update user email
    if 'email' in data and user:
        user.email = data['email']
    
    db.session.commit()
    
    return jsonify({'message': 'Profile updated successfully'}), 200
