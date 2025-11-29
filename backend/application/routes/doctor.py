from flask import Blueprint, jsonify, request
from application.models import Appointment, Treatment, Availability, Patient, Doctor, User
from application.database import db
from datetime import datetime, date, timedelta
from collections import Counter
from flask import render_template
from flask_mail import Message
from application.tasks import mail

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

@doctor_bp.route('/monthly-report/<int:doctor_id>', methods=['POST'])
def generate_monthly_report(doctor_id):
    """Generate and send monthly report for a specific doctor"""
    try:
        doctor = Doctor.query.get_or_404(doctor_id)
        
        # Calculate last month's date range
        today = date.today()
        first_day_this_month = today.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        first_day_last_month = last_day_last_month.replace(day=1)
        month_year = last_day_last_month.strftime('%B %Y')
        
        # Get appointments for last month
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.date >= first_day_last_month,
            Appointment.date <= today
        ).all()
        
        if not appointments:
            return jsonify({
                'message': f'No appointments found for {month_year}',
                'status': 'info'
            }), 200
        
        # Calculate statistics
        total_appointments = len(appointments)
        completed = sum(1 for a in appointments if a.status == 'Completed')
        cancelled = sum(1 for a in appointments if a.status == 'Cancelled')
        
        # Get diagnoses from treatments
        diagnoses = []
        for apt in appointments:
            if apt.treatment and apt.treatment.diagnosis:
                diagnoses.append(apt.treatment.diagnosis)
        
        diagnosis_counts = Counter(diagnoses)
        top_diagnoses = [{'name': d, 'count': c} for d, c in diagnosis_counts.most_common(5)]
        
        # Prepare appointment data for table
        apt_data = []
        for apt in appointments[:20]:  # Limit to 20 for email
            diagnosis = apt.treatment.diagnosis if apt.treatment else 'N/A'
            apt_data.append({
                'date': apt.date.strftime('%Y-%m-%d'),
                'patient': apt.patient.name,
                'diagnosis': diagnosis,
                'status': apt.status
            })
        
        # Get doctor email
        user = User.query.get(doctor.user_id)
        if not user or not user.username:
            return jsonify({'message': 'Doctor email not found'}), 404
        
        # Render email template
        html_body = render_template('email/monthly_report.html',
            doctor_name=doctor.name,
            month_year=month_year,
            total_appointments=total_appointments,
            completed_appointments=completed,
            cancelled_appointments=cancelled,
            appointments=apt_data,
            diagnoses=top_diagnoses,
            report_date=datetime.now().strftime('%B %d, %Y')
        )
        
        # Send email
        msg = Message(
            subject=f'Monthly Activity Report - {month_year}',
            recipients=[user.username],
            html=html_body
        )
        mail.send(msg)
        
        return jsonify({
            'message': f'Monthly report for {month_year} sent successfully to {user.username}',
            'status': 'success',
            'stats': {
                'total': total_appointments,
                'completed': completed,
                'cancelled': cancelled,
                'month': month_year
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error generating report: {str(e)}', 'status': 'error'}), 500
