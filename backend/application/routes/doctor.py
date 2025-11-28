from flask import Blueprint, jsonify, request
from application.models import Appointment, Treatment, Availability, Patient, Doctor
from application.database import db
from datetime import datetime

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/appointments/<int:doctor_id>', methods=['GET'])
def get_appointments(doctor_id):
    appointments = Appointment.query.filter_by(doctor_id=doctor_id, status='Booked').order_by(Appointment.date).all()
    return jsonify([{
        'id': a.id, 
        'patient': a.patient.name, 
        'date': str(a.date), 
        'time': str(a.time),
        'reason': a.reason or 'Not specified'
    } for a in appointments])

@doctor_bp.route('/assigned_patients/<int:doctor_id>', methods=['GET'])
def get_assigned_patients(doctor_id):
    # Get patients who have at least one appointment with this doctor
    appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
    patient_ids = set([a.patient_id for a in appointments])
    patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()
    return jsonify([{'id': p.id, 'name': p.name} for p in patients])

@doctor_bp.route('/patient_history/<int:patient_id>', methods=['GET'])
def get_patient_history(patient_id):
    appointments = Appointment.query.filter_by(patient_id=patient_id, status='Completed').all()
    history = []
    for app in appointments:
        if app.treatment:
            history.append({
                'id': app.treatment.id,  # Added treatment ID for editing
                'appointment_id': app.id,
                'date': str(app.date),
                'doctor': app.doctor.name,
                'diagnosis': app.treatment.diagnosis,
                'prescription': app.treatment.prescription,
                'notes': app.treatment.notes
            })
    return jsonify(history)

@doctor_bp.route('/availability', methods=['POST'])
def add_availability():
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    date_str = data.get('date')
    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')
    
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    start_time_obj = datetime.strptime(start_time_str, '%H:%M').time()
    end_time_obj = datetime.strptime(end_time_str, '%H:%M').time()
    
    avail = Availability(doctor_id=doctor_id, date=date_obj, start_time=start_time_obj, end_time=end_time_obj)
    db.session.add(avail)
    db.session.commit()
    return jsonify({'message': 'Availability added'}), 201

@doctor_bp.route('/availability/<int:doctor_id>/<date>/<time>', methods=['DELETE'])
def remove_availability(doctor_id, date, time):
    """Remove an availability slot"""
    date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    time_obj = datetime.strptime(time, '%H:%M').time()
    
    # Find the availability slot
    avail = Availability.query.filter_by(
        doctor_id=doctor_id,
        date=date_obj,
        start_time=time_obj,
        is_booked=False  # Only allow deletion of unbooked slots
    ).first()
    
    if avail:
        db.session.delete(avail)
        db.session.commit()
        return jsonify({'message': 'Availability removed'}), 200
    else:
        return jsonify({'message': 'Slot not found or already booked'}), 404

@doctor_bp.route('/appointments/<int:id>/cancel', methods=['PUT'])
def cancel_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    
    # Free up the availability slot
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

@doctor_bp.route('/treatment', methods=['POST'])
def add_treatment():
    data = request.get_json()
    appointment_id = data.get('appointment_id')
    diagnosis = data.get('diagnosis')
    prescription = data.get('prescription')
    
    treatment = Treatment(appointment_id=appointment_id, diagnosis=diagnosis, prescription=prescription)
    db.session.add(treatment)
    
    appointment = Appointment.query.get(appointment_id)
    appointment.status = 'Completed'
    db.session.commit()
    
    return jsonify({'message': 'Treatment added'}), 201

@doctor_bp.route('/treatment/<int:treatment_id>', methods=['PUT'])
def update_treatment(treatment_id):
    """Update existing treatment record"""
    treatment = Treatment.query.get_or_404(treatment_id)
    data = request.get_json()
    
    # Update treatment fields
    if 'diagnosis' in data:
        treatment.diagnosis = data['diagnosis']
    if 'prescription' in data:
        treatment.prescription = data['prescription']
    if 'notes' in data:
        treatment.notes = data['notes']
    
    db.session.commit()
    return jsonify({'message': 'Treatment updated successfully'}), 200
