
from celery import Celery
from flask import render_template
from flask_mail import Mail, Message
from datetime import datetime, date, timedelta
from collections import Counter
import csv
import os
import application.config as config
from application.models import Appointment, Doctor, Patient, Treatment, User
from application.database import db


celery = Celery('tasks',
                broker=config.CELERY_BROKER_URL,
                backend=config.CELERY_RESULT_BACKEND)

celery.conf.update(
    task_serializer=config.CELERY_TASK_SERIALIZER,
    result_serializer=config.CELERY_RESULT_SERIALIZER,
    accept_content=config.CELERY_ACCEPT_CONTENT,
    timezone=config.CELERY_TIMEZONE,
    enable_utc=config.CELERY_ENABLE_UTC
)
mail = None

def init_mail(app):
    
    global mail
    mail = Mail(app)

@celery.task(name='tasks.send_booking_confirmation')
def send_booking_confirmation(appointment_id):
    """Send booking confirmation email to patient"""
    from app import create_app
    app, _ = create_app()
    
    with app.app_context():
        try:
            appointment = Appointment.query.get(appointment_id)
            if not appointment:
                return "Appointment not found"
                
            patient = appointment.patient
            doctor = appointment.doctor
            user = User.query.get(patient.user_id)
            
            if not user or not user.username:
                return "User email not found"
                
            html_body = render_template('email/booking_confirmation.html',
                patient_name=patient.name,
                doctor_name=doctor.name,
                appointment_date=appointment.date.strftime('%B %d, %Y'),
                appointment_time=appointment.time.strftime('%I:%M %p'),
                reason=appointment.reason or 'General Consultation'
            )
            
            msg = Message(
                subject='Appointment Confirmation',
                recipients=[user.email],
                html=html_body
            )
            mail.send(msg)
            return f"Sent confirmation to {user.username}"
            
        except Exception as e:
            return f"Error sending confirmation: {str(e)}"

@celery.task(name='tasks.send_daily_reminders')
def send_daily_reminders():
    
    from app import create_app
    app, _ = create_app()
    
    with app.app_context():
        today = date.today()
        appointments = Appointment.query.filter_by(
            date=today,
            status='Booked'
        ).all()
        
        sent_count = 0
        for appointment in appointments:
            try:
                patient = appointment.patient
                doctor = appointment.doctor
                user = User.query.get(patient.user_id)
                if not user or not user.email: 
                    continue
                
            
                html_body = render_template('email/appointment_reminder.html',
                    patient_name=patient.name,
                    doctor_name=doctor.name,
                    appointment_date=appointment.date.strftime('%B %d, %Y'),
                    appointment_time=appointment.time.strftime('%I:%M %p'),
                    reason=appointment.reason or 'General Consultation'
                )
                
                msg = Message(
                    subject='Appointment Reminder - Today',
                    recipients=[user.email],
                    html=html_body
                )
                mail.send(msg)
                sent_count += 1
                
            except Exception as e:
                print(f"Error sending reminder to {patient.name}: {str(e)}")
                continue
        return f"Sent {sent_count} reminders for {len(appointments)} appointments"

@celery.task(name='tasks.send_monthly_reports')
def send_monthly_reports():
    """Send monthly activity reports to all doctors"""
    from app import create_app
    app, _ = create_app()
    
    with app.app_context():
        
        today = date.today()
        first_day_this_month = today.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        first_day_last_month = last_day_last_month.replace(day=1)
        
        month_year = last_day_last_month.strftime('%B %Y')
        
        doctors = Doctor.query.all()
        sent_count = 0
        
        for doctor in doctors:
            try:
                
                appointments = Appointment.query.filter(
                    Appointment.doctor_id == doctor.id,
                    Appointment.date >= first_day_last_month,
                    Appointment.date <= last_day_last_month
                ).all()
                
                if not appointments:
                    continue 
                
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
                if not user or not user.email:
                    continue
                
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
                    recipients=[user.email],
                    html=html_body
                )
                mail.send(msg)
                sent_count += 1
                
            except Exception as e:
                print(f"Error sending report to Dr. {doctor.name}: {str(e)}")
                continue
        
        return f"Sent {sent_count} monthly reports to doctors"

@celery.task(name='tasks.export_patient_treatments', bind=True)
def export_patient_treatments(self, patient_id):
    """Export patient treatment history as CSV"""
    from app import create_app
    app, _ = create_app()
    
    with app.app_context():
        try:
            patient = Patient.query.get(patient_id)
            if not patient:
                return {'status': 'error', 'message': 'Patient not found'}
            
            # Get all treatments for patient
            treatments = Treatment.query.join(Appointment).filter(Appointment.patient_id == patient_id).all()
            
            # Creating exports directory if it doesn't exist
            os.makedirs(config.EXPORT_FOLDER, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'patient_{patient_id}_treatments_{timestamp}.csv'
            filepath = os.path.join(config.EXPORT_FOLDER, filename)
            
            # CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'Patient ID', 'Patient Name', 'Doctor Name',
                    'Appointment Date', 'Appointment Time', 'Diagnosis',
                    'Prescription', 'Notes'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for treatment in treatments:
                    appointment = treatment.appointment
                    doctor = appointment.doctor if appointment else None
                    
                    writer.writerow({
                        'Patient ID': patient.id,
                        'Patient Name': patient.name,
                        'Doctor Name': doctor.name if doctor else 'N/A',
                        'Appointment Date': appointment.date if appointment else 'N/A',
                        'Appointment Time': appointment.time if appointment else 'N/A',
                        'Diagnosis': treatment.diagnosis or '',
                        'Prescription': treatment.prescription or '',
                        'Notes': treatment.notes or ''
                    })
            
            return {
                'status': 'success',
                'filename': filename,
                'filepath': filepath,
                'record_count': len(treatments)
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
