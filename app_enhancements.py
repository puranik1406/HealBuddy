# Additional models and routes for HealBuddy enhancements
# Add this code to app.py

# NEW MODEL: Add this after the Consultation model
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    consultation_id = db.Column(db.Integer, db.ForeignKey('consultation.id'))
    appointment_type = db.Column(db.String(20), default='online')  # online, offline
    appointment_date = db.Column(db.DateTime)
    appointment_slot = db.Column(db.String(50))  # e.g., "09:00-10:00"
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    patient = db.relationship('User', foreign_keys=[patient_id], backref='patient_appointments')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_appointments')

# Severity classification helper
def get_severity_classification(pain_level):
    """Return proper severity classification"""
    if pain_level >= 9:
        return "Emergency"
    elif pain_level >= 7:
        return "High Risk"
    elif pain_level >= 4:
        return "Moderate Risk"
    else:
        return "Mild Risk"

# Pharmacy data (hardcoded for MVP - can be moved to database later)
PHARMACIES = [
    {
        "name": "Apollo Pharmacy",
        "address": "123 Main Street, Downtown",
        "phone": "+91 98765 43210",
        "distance": "0.5 km"
    },
    {
        "name": "MedPlus",
        "address": "456 Park Avenue, City Center",
        "phone": "+91 98765 43211",
        "distance": "1.2 km"
    },
    {
        "name": "HealthCare Pharmacy",
        "address": "789 Hospital Road, Medical District",
        "phone": "+91 98765 43212",
        "distance": "2.0 km"
    }
]

#=======================================
# NEW ROUTES
#=======================================

@app.route('/get_doctors', methods=['GET'])
@login_required
def get_doctors():
    """Get list of available doctors"""
    doctors = User.query.filter_by(user_type='doctor').all()
    return jsonify([{
        'id': d.id,
        'name': f"Dr. {d.first_name} {d.last_name}",
        'specialization': d.specialization or 'General Physician',
        'experience': d.years_of_experience or 0,
        'hospital': d.hospital_affiliation or 'Independent Practice',
        'fee': d.consultation_fee or 500
    } for d in doctors])

@app.route('/get_pharmacies', methods=['GET'])
@login_required
def get_pharmacies():
    """Get list of nearby pharmacies"""
    return jsonify(PHARMACIES)

@app.route('/book_appointment', methods=['POST'])
@login_required
def book_appointment():
    """Book an appointment with a doctor"""
    if current_user.user_type != 'patient':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.json
        appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=data['doctor_id'],
            consultation_id=data.get('consultation_id'),
            appointment_type=data.get('appointment_type', 'online'),
            appointment_date=datetime.strptime(data['appointment_date'], '%Y-%m-%d'),
            appointment_slot=data['appointment_slot']
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Appointment booked successfully',
            'appointment_id': appointment.id
        })
    except Exception as e:
        print(f"Error booking appointment: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/view_patient/<int:patient_id>')
@login_required
def view_patient(patient_id):
    """View detailed patient information (for doctors/hospitals)"""
    if current_user.user_type not in ['doctor', 'hospital']:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    patient = User.query.get_or_404(patient_id)
    if patient.user_type != 'patient':
        flash('Invalid patient ID')
        return redirect(url_for('dashboard'))
    
    # Get patient's consultations and health records
    consultations = Consultation.query.filter_by(patient_id=patient_id).order_by(Consultation.created_at.desc()).all()
    health_records = HealthRecord.query.filter_by(patient_id=patient_id).order_by(HealthRecord.uploaded_at.desc()).all()
    
    # Calculate age if DOB is available
    age = None
    if patient.date_of_birth:
        today = datetime.today()
        age = today.year - patient.date_of_birth.year - ((today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day))
    
    return render_template('view_patient.html', 
                         patient=patient, 
                         consultations=consultations,
                         health_records=health_records,
                         age=age)

@app.route('/doctor_schedule')
@login_required
def doctor_schedule():
    """View doctor's schedule"""
    if current_user.user_type != 'doctor':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    appointments = Appointment.query.filter_by(doctor_id=current_user.id).order_by(Appointment.appointment_date).all()
    return render_template('doctor_schedule.html', appointments=appointments)
