from app import create_app
from application.models import User, Doctor, Patient, Appointment, Treatment
from application.database import db
from datetime import date, timedelta, datetime
from collections import Counter
from flask import render_template
from flask_mail import Message
from application.tasks import mail

app, _ = create_app()

with app.app_context():
    
    
    # Get a doctor (or create test data if needed)
    doctor = Doctor.query.first()
    
    if not doctor:
        print("No doctor found in database. Creating test doctor...")
        # Create test doctor
        user = User(username="test_doctor", email="aryanmishra1411@zohomail.in", role='doctor')
        user.set_password("password")
        db.session.add(user)
        db.session.commit()
        
        doctor = Doctor(user_id=user.id, name="Dr. Test Doctor", specialization="General", department="General")
        db.session.add(doctor)
        db.session.commit()
        print(f"Created test doctor: {doctor.name}")
    
    # Calculate last month's date range
    today = date.today()
    first_day_this_month = today.replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    first_day_last_month = last_day_last_month.replace(day=1)
    month_year = last_day_last_month.strftime('%B %Y')
    
    print(f"Generating report for: {month_year}")
    
    # Get appointments for last month
    appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.date >= first_day_last_month,
        Appointment.date <= last_day_last_month
    ).all()
    
    print(f"Found {len(appointments)} appointments for last month")
    
    # If no appointments, create some test data
    if not appointments:
        print("No appointments found. Creating test appointment...")
        patient = Patient.query.first()
        
        if not patient:
            print("No patient found. Creating test patient...")
            patient_user = User(username="test_patient", email="patient@test.com", role='patient')
            patient_user.set_password("password")
            db.session.add(patient_user)
            db.session.commit()
            
            patient = Patient(
                user_id=patient_user.id,
                name="Test Patient",
                age=30,
                gender="Male",
                contact="1234567890",
                address="Test Address"
            )
            db.session.add(patient)
            db.session.commit()
        
        # Create test appointment in last month
        last_month_date = first_day_last_month + timedelta(days=10)
        apt = Appointment(
            doctor_id=doctor.id,
            patient_id=patient.id,
            date=last_month_date,
            time=datetime.strptime("10:00", "%H:%M").time(),
            status="Completed",
            reason="General Checkup"
        )
        db.session.add(apt)
        db.session.commit()
        
        # Add treatment
        treatment = Treatment(
            appointment_id=apt.id,
            diagnosis="Common Cold",
            prescription="Rest and fluids",
            notes="Patient recovering well"
        )
        db.session.add(treatment)
        db.session.commit()
        
        appointments = [apt]
        print(f"Created test appointment on {last_month_date}")
    
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
    
    # Send email to specified address
    recipient_email = "aryanmishra1411@zohomail.in"
    msg = Message(
        subject=f'Monthly Activity Report - {month_year}',
        recipients=[recipient_email],
        html=html_body
    )
    
    try:
        mail.send(msg)
        print(f"✅ Successfully sent monthly report to {recipient_email}")
        print(f"Report contains:")
        print(f"  - Total Appointments: {total_appointments}")
        print(f"  - Completed: {completed}")
        print(f"  - Cancelled: {cancelled}")
        print(f"  - Top Diagnoses: {len(top_diagnoses)}")
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
