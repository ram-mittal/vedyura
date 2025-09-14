import json
from flask import Flask, render_template, request, redirect, url_for, session, flash

# Initialize the Flask application
app = Flask(__name__)
# A secret key is needed to keep the user's session secure.
app.secret_key = 'your_super_secret_key' 

# --- Helper Functions to Read/Write JSON Data ---

def load_users():
    """Loads user data from the users.json file."""
    try:
        with open('data/users.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def load_requests():
    """Loads consultation requests from the requests.json file."""
    try:
        with open('data/requests.json', 'r') as f:
            return json.load(f)
    # CORRECTED: If file is empty or missing, return the correct base structure
    except (FileNotFoundError, json.JSONDecodeError):
        return {"requests": []}

def save_requests(requests_data):
    """Saves the consultation requests data to the requests.json file."""
    with open('data/requests.json', 'w') as f:
        json.dump(requests_data, f, indent=4)

# --- Public Page Routes ---

@app.route('/')
def home():
    """Renders the home page."""
    return render_template('home.html')

@app.route('/contact')
def contact_us():
    """Renders the contact us page."""
    return render_template('contact_us.html')

@app.route('/signup')
def signup():
    """Renders the main sign-up/sign-in page."""
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """Logs the user out by clearing the session."""
    session.clear()
    return redirect(url_for('home'))

# --- Doctor Authentication and Dashboard Routes ---

@app.route('/doctor/login', methods=['POST'])
def doctor_login():
    """Handles the doctor login form submission."""
    user_id = request.form.get('user_id')
    password = request.form.get('password')
    
    users = load_users()
    for user in users:
        # Compare submitted data as strings to match JSON data types
        if user.get('role') == 'doctor' and str(user.get('id')) == user_id and str(user.get('password')) == password:
            session['user_id'] = user_id
            session['role'] = 'doctor'
            return redirect(url_for('doctor_dashboard'))
    
    flash('Invalid credentials. Please try again.', 'error')
    return redirect(url_for('signup'))

@app.route('/doctor/dashboard')
def doctor_dashboard():
    """Renders the doctor's main dashboard page."""
    if 'user_id' in session and session.get('role') == 'doctor':
        return render_template('doctor_dashboard.html')
    return redirect(url_for('signup'))

@app.route('/doctor/requests')
def doctor_patient_requests():
    """Renders the page that lists patient requests for the doctor."""
    if 'user_id' in session and session.get('role') == 'doctor':
        all_requests_data = load_requests()
        # CORRECTED: Pass the list of requests, not the whole dictionary
        return render_template('doctor_patient_requests.html', requests=all_requests_data.get('requests', []))
    return redirect(url_for('signup'))

@app.route('/doctor/diet-chart')
def doctor_diet_chart():
    """Renders the diet chart creation page for the doctor."""
    if 'user_id' in session and session.get('role') == 'doctor':
        return render_template('doctor_diet_chart.html')
    return redirect(url_for('signup'))

@app.route('/doctor/profile')
def doctor_profile():
    """Renders the doctor's profile page."""
    if 'user_id' in session and session.get('role') == 'doctor':
        return render_template('doctor_profile.html')
    return redirect(url_for('signup'))

# --- Patient Authentication and Dashboard Routes ---

@app.route('/patient/bypass')
def patient_bypass_login():
    """Allows a patient to bypass login for development purposes."""
    session['user_id'] = 'bypassed_user' # A simple identifier for a guest user
    session['role'] = 'patient'
    return redirect(url_for('patient_dashboard'))

@app.route('/patient/dashboard')
def patient_dashboard():
    """Renders the patient's main dashboard page."""
    if 'user_id' in session and session.get('role') == 'patient':
        return render_template('patient_dashboard.html')
    return redirect(url_for('signup'))

@app.route('/patient/self-diagnosis')
def patient_self_diagnosis():
    """Renders the self-diagnosis page for the patient."""
    if 'user_id' in session and session.get('role') == 'patient':
        return render_template('patient_self_diagnosis.html')
    return redirect(url_for('signup'))

@app.route('/patient/consult-doctor')
def patient_consult_doctor():
    """Renders the page for patients to find and consult doctors."""
    if 'user_id' in session and session.get('role') == 'patient':
        all_users = load_users()
        # Safely filter for users who are doctors
        doctors = [user for user in all_users if isinstance(user, dict) and user.get('role') == 'doctor']
        return render_template('patient_consult_doctor.html', doctors=doctors)
    return redirect(url_for('signup'))

@app.route('/patient/send-request', methods=['POST'])
def send_request():
    """Handles the form submission when a patient sends a consultation request."""
    if 'user_id' in session and session.get('role') == 'patient':
        doctor_id = request.form.get('doctor_id')
        patient_id = session['user_id']
        
        all_requests_data = load_requests()
        
        new_request = {
            'doctor_id': doctor_id,
            'patient_id': patient_id,
            'status': 'pending' # Initial status of any new request
        }
        
        # CORRECTED: Append to the 'requests' list inside the dictionary
        all_requests_data['requests'].append(new_request)
        save_requests(all_requests_data)
        
        return redirect(url_for('patient_consult_doctor'))
    return redirect(url_for('signup'))


@app.route('/patient/profile')
def patient_profile():
    """Renders the patient's profile page."""
    if 'user_id' in session and session.get('role') == 'patient':
        return render_template('patient_profile.html')
    return redirect(url_for('signup'))

# This allows the script to be run directly
if __name__ == '__main__':
    app.run(debug=True)
