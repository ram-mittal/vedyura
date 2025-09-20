import json
import time
import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response, make_response
from scipy import signal
from scipy.fft import fft, fftfreq
from fpdf import FPDF

# --- Vedyura Core Imports ---
from personal_diet_tool import get_tool_response
from health_analyzer import generate_health_profile, determine_dominant_dosha

# Initialize the Flask application
app = Flask(__name__)
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
            data = json.load(f)
            return data if isinstance(data, dict) and 'requests' in data else {'requests': []}
    except (FileNotFoundError, json.JSONDecodeError):
        return {'requests': []}

def save_requests(requests_data):
    """Saves the consultation requests data to the requests.json file."""
    with open('data/requests.json', 'w') as f:
        json.dump(requests_data, f, indent=4)


# --- Public & Core App Routes (Unchanged) ---

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/contact')
def contact_us():
    return render_template('contact_us.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/predict', methods=['POST'])
def predict():
    text = request.get_json().get("message")
    user_id = session.get('user_id', 'anonymous_user')
    user_session_data = {
        'form_data': session.get('form_data'),
        'ppg_results': session.get('ppg_results')
    }
    response = get_tool_response(user_id, text, user_session_data)
    return jsonify({"answer": response})

# (All other Doctor and Patient routes like login, dashboards, etc. remain here, unchanged)
@app.route('/doctor/login', methods=['POST'])
def doctor_login():
    """Handles the doctor login form submission."""
    user_id = request.form.get('user_id')
    password = request.form.get('password')

    users = load_users()
    for user in users:
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
        doctor_id = session['user_id']
        all_requests_data = load_requests()
        all_users = load_users()

        # Helper to get user details by ID
        def get_user_by_id(user_id):
            for user in all_users:
                if str(user.get('id')) == str(user_id):
                    return user
            return None

        # Filter requests for the logged-in doctor
        pending_requests = []
        current_patients = []
        # FIX: Iterate over the list of requests, not the dictionary keys.
        for req in all_requests_data.get('requests', []):
            if str(req.get('doctor_id')) == str(doctor_id):
                patient = get_user_by_id(req.get('patient_id'))
                if patient:
                    if req.get('status') == 'pending':
                        pending_requests.append({'request': req, 'patient': patient})
                    elif req.get('status') == 'accepted':
                        current_patients.append(patient)
        return render_template('doctor_patient_requests.html', pending_requests=pending_requests, current_patients=current_patients)
    return redirect(url_for('signup'))

@app.route('/doctor/diet-chart')
def doctor_diet_chart():
    """Renders the diet chart creation page for the doctor."""
    if 'user_id' in session and session.get('role') == 'doctor':
        doctor_id = session['user_id']
        all_requests_data = load_requests()
        all_users = load_users()

        def get_user_by_id(user_id):
            for user in all_users:
                if str(user.get('id')) == str(user_id):
                    return user
            return None

        current_patients = []
        for req in all_requests_data.get('requests', []):
            if str(req.get('doctor_id')) == str(doctor_id) and req.get('status') == 'accepted':
                patient = get_user_by_id(req.get('patient_id'))
                if patient:
                    try:
                        with open(f'data/patient_diagnosis_{patient["id"]}.json', 'r') as f:
                            diagnosis_data = json.load(f)
                        
                        form_data = diagnosis_data.get('form_data', {})
                        ppg_results = diagnosis_data.get('ppg_results', {})
                        
                        health_profile = generate_health_profile(form_data, ppg_results)

                        patient['diagnosis'] = {
                            'dominant_dosha': diagnosis_data.get('dominant_dosha', 'N/A'),
                            'health_goals': form_data.get('health_goal', 'N/A'),
                            'dietary_preferences': form_data.get('dietary_preferences', 'N/A'),
                            'allergies': form_data.get('allergies', 'N/A'),
                            'bmi_value': health_profile.get('bmi_value', 'N/A'),
                            'bmi_category': health_profile.get('bmi_category', 'Not Calculated'),
                            'heart_rate': int(health_profile.get('heart_rate')) if health_profile.get('heart_rate') else "N/A",
                            'protein_target': health_profile.get('protein_target', 'Not Calculated')
                        }
                    except (FileNotFoundError, json.JSONDecodeError):
                        patient['diagnosis'] = None
                    current_patients.append(patient)

        return render_template('doctor_diet_chart.html', current_patients=current_patients)
    return redirect(url_for('signup'))

@app.route('/doctor/generate-diet-chart-pdf', methods=['POST'])
def generate_doctor_diet_chart_pdf():
    if 'user_id' not in session or session.get('role') != 'doctor':
        return redirect(url_for('signup'))

    patient_id = request.form.get('patient_id')
    patient_info = {
        'id': patient_id,
        'name': 'John Doe',
        'age': 35,
    }

    meal_plan = {
        'Breakfast': {
            'items': request.form.get('breakfast_items'),
            'advice': request.form.get('breakfast_advice')
        },
        'Lunch': {
            'items': request.form.get('lunch_items'),
            'advice': request.form.get('lunch_advice')
        },
        'Dinner': {
            'items': request.form.get('dinner_items'),
            'advice': request.form.get('dinner_advice')
        },
        'Snacks': {
            'items': request.form.get('snacks_items'),
            'advice': request.form.get('snacks_advice')
        }
    }
    professional_advice = request.form.get('professional_advice')

    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 16)
            self.set_text_color(34, 139, 34)
            self.cell(0, 10, 'Vedyura - Doctor\'s Diet Plan', 0, 1, 'C')
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

        def section_title(self, title):
            self.set_font('Arial', 'B', 12)
            self.set_fill_color(200, 220, 200)
            self.set_text_color(0, 0, 0)
            self.cell(0, 8, title, 0, 1, 'L', fill=True)
            self.ln(4)

        def section_body(self, body):
            # Ensure body is a string and handle potential encoding issues
            if not isinstance(body, str):
                body = str(body)
            body = body.encode('latin-1', 'replace').decode('latin-1')
            self.set_font('Arial', '', 11)
            self.set_text_color(0, 0, 0)
            self.multi_cell(0, 6, body)
            self.ln()

    pdf = PDF()
    pdf.add_page()

    pdf.section_title(f"Diet Plan for {patient_info['name']}")
    
    for meal, details in meal_plan.items():
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, meal, 0, 1, 'L')
        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(0, 6, f"**Items:** {details['items']}")
        pdf.multi_cell(0, 6, f"**Advice:** {details['advice']}")
        pdf.ln(2)

    pdf.section_title('Professional Advice')
    pdf.section_body(professional_advice)

    pdf.section_title('Disclaimer')
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 5, 'This diet chart is a recommendation based on the information provided. Please consult with your doctor for any further questions.')

    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    response = make_response(pdf_bytes)
    response.headers.set('Content-Disposition', 'attachment', filename=f'Diet_Chart_{patient_info["name"].replace(" ", "_")}.pdf')
    response.headers.set('Content-Type', 'application/pdf')

    return response

@app.route('/doctor/profile')
def doctor_profile():
    """Renders the doctor's profile page."""
    if 'user_id' in session and session.get('role') == 'doctor':
        return render_template('doctor_profile.html')
    return redirect(url_for('signup'))

@app.route('/doctor/handle-request', methods=['POST'])
def handle_patient_request():
    """Handles accepting or declining a patient request."""
    if 'user_id' not in session or session.get('role') != 'doctor':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid request'}), 400

    patient_id = data.get('patient_id')
    action = data.get('action')
    doctor_id = session['user_id']

    all_requests_data = load_requests()
    requests_list = all_requests_data.get('requests', [])
    
    request_updated = False
    for req in requests_list:
        if str(req.get('patient_id')) == str(patient_id) and str(req.get('doctor_id')) == str(doctor_id) and req.get('status') == 'pending':
            if action == 'accept':
                req['status'] = 'accepted'
                request_updated = True
            elif action == 'decline':
                req['status'] = 'declined'
                request_updated = True
            
            if request_updated:
                save_requests(all_requests_data)
                
                if action == 'accept':
                    all_users = load_users()
                    patient_details = next((user for user in all_users if str(user.get('id')) == str(patient_id)), None)
                    if patient_details:
                        return jsonify({'success': True, 'patient': patient_details})
                    else:
                        return jsonify({'success': False, 'message': 'Patient not found.'})

                return jsonify({'success': True})

    return jsonify({'success': False, 'message': 'Request not found or already handled.'})


@app.route('/doctor/remove-patient', methods=['POST'])
def remove_patient():
    """Handles removing a patient from the doctor's current patient list."""
    if 'user_id' not in session or session.get('role') != 'doctor':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid request'}), 400

        patient_id = data.get('patient_id')
        doctor_id = session['user_id']

        all_requests_data = load_requests()
        requests_list = all_requests_data.get('requests', [])
        
        request_updated = False
        for req in requests_list:
            if str(req.get('patient_id')) == str(patient_id) and str(req.get('doctor_id')) == str(doctor_id) and req.get('status') == 'accepted':
                req['status'] = 'declined'
                request_updated = True
                break
        
        if request_updated:
            save_requests(all_requests_data)
            return jsonify({'success': True})

        return jsonify({'success': False, 'message': 'Patient not found in your list.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# --- Patient Authentication and Dashboard Routes ---

@app.route('/patient/login', methods=['POST'])
def patient_login():
    """Handles the patient login form submission."""
    user_id = request.form.get('user_id')
    password = request.form.get('password')

    users = load_users()
    for user in users:
        if user.get('role') == 'patient' and str(user.get('id')) == user_id and str(user.get('password')) == password:
            session['user_id'] = user_id
            session['role'] = 'patient'
            return redirect(url_for('patient_dashboard'))

    flash('Invalid credentials. Please try again.', 'error')
    return redirect(url_for('signup'))

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
            'status': 'pending'
        }

        all_requests_data['requests'].append(new_request)
        save_requests(all_requests_data)

        flash('Your request has been sent successfully!', 'success')
        return redirect(url_for('patient_consult_doctor'))
    return redirect(url_for('signup'))


@app.route('/patient/profile')
def patient_profile():
    """Renders the patient's profile page."""
    if 'user_id' in session and session.get('role') == 'patient':
        return render_template('patient_profile.html')
    return redirect(url_for('signup'))

@app.route('/patient/save-form-data', methods=['POST'])
def save_form_data():
    """Saves the detailed form data and determined dosha to a file."""
    if 'user_id' in session and session.get('role') == 'patient':
        form_data = request.form.to_dict()
        dominant_dosha = determine_dominant_dosha(form_data)

        patient_id = session['user_id']
        # Combine form data with existing PPG data if it exists
        diagnosis_data = {'form_data': form_data, 'dominant_dosha': dominant_dosha}
        
        # Preserve PPG results if they are already in the session
        if 'ppg_results' in session:
            diagnosis_data['ppg_results'] = session['ppg_results']

        try:
            # Save the combined data to a file
            with open(f'data/patient_diagnosis_{patient_id}.json', 'w') as f:
                json.dump(diagnosis_data, f, indent=4)
        except IOError as e:
            return jsonify({'status': 'error', 'message': f'Could not save data: {e}'})

        # Update session data
        session['form_data'] = form_data
        session['dominant_dosha'] = dominant_dosha
        session.modified = True

        return jsonify({'status': 'success', 'message': 'Form data saved.'})
    return jsonify({'status': 'error', 'message': 'User not logged in.'})

# --- <<<<<<<<<<<<<<<<<<<<<<<< MODIFIED SECTION STARTS HERE >>>>>>>>>>>>>>>>>>>>>>>> ---

@app.route('/patient/generate-diet-chart')
def generate_diet_chart_pdf():
    """
    Generates a diet chart PDF that now INCLUDES the detailed
    Ayurvedic pulse analysis from the new PPG model.
    """
    if 'user_id' not in session:
        return redirect(url_for('signup'))

    form_data = session.get('form_data')
    ppg_results = session.get('ppg_results', {}) # Get the new detailed PPG results

    if not form_data:
        flash("Please complete the self-diagnosis form first.", "error")
        return redirect(url_for('patient_self_diagnosis'))
    
    # This function from health_analyzer.py should ideally combine form and PPG data
    health_profile = generate_health_profile(form_data, ppg_results)

    # Define the PDF structure
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 16)
            self.set_text_color(34, 139, 34)
            self.cell(0, 10, 'Vedyura Personalized Health Plan', 0, 1, 'C')
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

        def section_title(self, title):
            self.set_font('Arial', 'B', 12)
            self.set_fill_color(200, 220, 200)
            self.cell(0, 8, title, 0, 1, 'L', fill=True)
            self.ln(4)

        def section_body(self, body):
            # Ensure body is a string and handle potential encoding issues
            if not isinstance(body, str):
                body = str(body)
            body = body.encode('latin-1', 'replace').decode('latin-1')
            self.set_font('Arial', '', 11)
            self.multi_cell(0, 6, body)
            self.ln()

    # --- PDF Generation ---
    pdf = PDF()
    pdf.add_page()

    # Section 1: General Health Profile
    pdf.section_title('Your Health Profile Summary')
    pdf.section_body(health_profile.get('profile_summary', 'Summary not available.'))

    # Section 2: Key Health Metrics
    pdf.section_title('Key Health Metrics')
    metrics_text = (
        f"Body Mass Index (BMI): {health_profile.get('bmi_value', 'N/A')} ({health_profile.get('bmi_category', 'N/A')})\n"
        f"Resting Heart Rate (from PPG): {ppg_results.get('heart_rate', 'N/A')} BPM\n"
        f"Estimated Daily Protein Intake: {health_profile.get('protein_target', 'N/A')}"
    )
    pdf.section_body(metrics_text)

    # --- NEW SECTION: Ayurvedic Pulse Analysis ---
    if ppg_results and 'dosha' in ppg_results:
        pdf.section_title('Ayurvedic Pulse Analysis (Nadi Pariksha)')
        
        dosha_name = ppg_results.get('dosha', 'N/A').capitalize()
        pulse_description = ppg_results.get('description', 'No analysis available.')
        
        analysis_text = f"**Pulse-Based Dosha:** {dosha_name}\n\n{pulse_description}"
        pdf.section_body(analysis_text)
        
        # Add the specific recommendations from the PPG analysis
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, "Recommendations based on your Pulse:", 0, 1, 'L')
        pdf.ln(2)
        
        recommendations = ppg_results.get('recommendations', [])
        for rec in recommendations:
            pdf.set_font('Arial', '', 11)
            # Add a bullet point character
            pdf.multi_cell(0, 6, f'- {rec}')
        pdf.ln(4)

    # Section 4: Meal Plan
    plan_title = 'Your Daily Meal Plan'
    if health_profile.get('plan_type') == 'weekly':
        plan_title = 'Your Weekly Meal Plan'
    pdf.section_title(f"{plan_title} (Approx. Target: {health_profile.get('calories', 'N/A')} kcal per day)")
    
    # --- FIX: Iterate over the list of meal dictionaries correctly ---
    meal_plan_data = health_profile.get('meal_plan', [])
    for meal_item in meal_plan_data:
        meal_name = meal_item.get('meal', 'N/A')
        food_description = meal_item.get('food', 'N/A')
        pdf.section_body(f"**{meal_name}:** {food_description}")


    # Section 5: General Lifestyle Recommendations
    pdf.section_title('Personalized Lifestyle Recommendations')
    pdf.section_body(health_profile.get('recommendations', 'No recommendations available.'))

    # Section 6: Disclaimer
    pdf.section_title('Disclaimer')
    pdf.set_font('Arial', 'I', 9)
    pdf.multi_cell(0, 5, health_profile.get('disclaimer', 'Standard disclaimer.'))

    # --- Create and return the response ---
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    response = make_response(pdf_bytes)
    response.headers.set('Content-Disposition', 'attachment', filename='Vedyura_Health_Plan.pdf')
    response.headers.set('Content-Type', 'application/pdf')
    return response

# --- <<<<<<<<<<<<<<<<<<<<<<<< MODIFIED SECTION ENDS HERE >>>>>>>>>>>>>>>>>>>>>>>> ---

@app.route('/patient/get-recipes')
def get_recipes():
    """
    Fetches recipes suitable for the patient's dominant dosha stored in the session.
    """
    if 'user_id' not in session or session.get('role') != 'patient':
        return jsonify({'error': 'Not authorized'}), 401

    if 'dominant_dosha' not in session:
        return jsonify({'error': 'Please complete the self-diagnosis test first.'}), 400

    dominant_dosha = session['dominant_dosha'].lower()

    try:
        with open('data/recipes.json', 'r', encoding='utf-8') as f:
            all_recipes = json.load(f)

        recommended_recipes = [
            recipe for recipe in all_recipes
            if recipe.get('properties', {}).get(dominant_dosha) in ['Decrease', 'Neutral']
        ]

        return jsonify({
            'count': len(recommended_recipes),
            'dosha': dominant_dosha.capitalize(),
            'recipes': recommended_recipes
        })

    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({'error': 'Recipe database not found.'}), 500


# ==============================================================================
# =========== ADVANCED PPG INTEGRATION - REPLACES OLD PPG CODE ===============
# ==============================================================================

# --- Global variables for the new PPG signal processing ---
red_values = []
green_values = []
blue_values = []
timestamps = []
fs = 30  # Assumed sampling frequency
start_time = time.time()
measurement_active = False
camera = None

# --- Liveness detection variables ---
liveness_check_active = False
liveness_check_passed = False
blink_detected = False
blink_start_time = 0

# --- Initialize face and eye cascade classifiers ---
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
eye_cascade_alt = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye_tree_eyeglasses.xml')


def bandpass_filter(data, lowcut, highcut, fs, order=5):
    """Applies a bandpass filter to the signal."""
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    y = signal.filtfilt(b, a, data)
    return y

def detect_liveness(face_roi):
    """Detects liveness by checking for eye blinks."""
    global blink_detected, blink_start_time
    eyes = eye_cascade.detectMultiScale(face_roi, 1.1, 4)
    if len(eyes) == 0: # If no eyes are detected, could be a blink
        if not blink_detected:
            blink_detected = True
            blink_start_time = time.time()
        elif time.time() - blink_start_time > 0.1: # Check if "blink" is of reasonable duration
             return True # Liveness confirmed
    else:
        blink_detected = False
    return False

def process_frame_advanced(frame):
    """Processes each frame for face detection, liveness check, and PPG signal extraction."""
    global liveness_check_passed, measurement_active
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    if not liveness_check_passed:
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            if detect_liveness(roi_gray):
                liveness_check_passed = True
                break # Exit after first liveness confirmation

    if liveness_check_passed:
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            forehead_roi = frame[y+h//10 : y+h//4, x+w//4 : x+3*w//4]
            if forehead_roi.size > 0 and measurement_active:
                b, g, r = cv2.split(forehead_roi)
                red_values.append(np.mean(r))
                green_values.append(np.mean(g))
                blue_values.append(np.mean(b))
                timestamps.append(time.time())
    elif len(faces) > 0:
         for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

    return frame

def generate_frames_advanced():
    """Generates video frames from the webcam with advanced processing."""
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        print("Error: Cannot open camera.")
        return

    while True:
        success, frame = camera.read()
        if not success:
            print("Error: Failed to grab a frame.")
            break
        
        processed_frame = process_frame_advanced(frame)
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        if not ret:
            continue
        
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

def calculate_heart_rate_advanced(signal_data, fs_est):
    """Calculates heart rate from the PPG signal using robust methods."""
    if len(signal_data) < fs_est * 2:
        return 0
    
    # 1. Preprocess: Detrend and filter
    detrended_signal = signal.detrend(signal_data)
    filtered_signal = bandpass_filter(detrended_signal, 0.8, 2.5, fs_est)

    # 2. Method 1: FFT-based heart rate
    n = len(filtered_signal)
    yf = fft(filtered_signal)
    xf = fftfreq(n, 1 / fs_est)
    mask = (xf > 0.8) & (xf < 2.5) # Typical HR frequency range
    if not any(mask): return 0
    
    fft_peak_index = np.argmax(np.abs(yf[mask]))
    hr_fft = xf[mask][fft_peak_index] * 60

    # 3. Method 2: Peak detection in time domain
    peaks, _ = signal.find_peaks(filtered_signal, distance=fs_est/2.5)
    if len(peaks) < 2:
        return hr_fft # Fallback to FFT result
    
    avg_interval = np.mean(np.diff(peaks)) / fs_est
    hr_peaks = 60 / avg_interval
    
    # 4. Combine and validate
    heart_rate = (hr_fft + hr_peaks) / 2
    return heart_rate if 40 < heart_rate < 180 else 0

def analyze_ayurvedic_profile(heart_rate):
    """Provides detailed Ayurvedic dosha analysis based on heart rate."""
    if 50 <= heart_rate < 70:
        dosha = 'kapha'
        description = "Your heart rate suggests a Kapha dominant constitution, characterized by a steady and strong pulse. You likely have good stamina and a calm nature."
        recs = ['Engage in regular, vigorous exercise.', 'Favor warm, light, and dry foods.', 'Incorporate stimulating spices like ginger and black pepper.']
    elif 70 <= heart_rate < 85:
        dosha = 'pitta'
        description = "Your heart rate indicates a Pitta dominant constitution, with a moderate and sharp pulse. You are likely intelligent, focused, and have strong digestion."
        recs = ['Engage in calming activities like swimming or walking in nature.', 'Favor cooling, sweet, and bitter foods.', 'Avoid excessive heat and spicy foods.']
    elif 85 <= heart_rate <= 100:
        dosha = 'vata'
        description = "Your heart rate points to a Vata dominant constitution, which can be quick and variable. You are likely creative, energetic, and quick-thinking."
        recs = ['Establish a regular daily routine.', 'Favor warm, moist, and grounding foods.', 'Practice calming exercises like yoga and meditation.']
    else:
        dosha = 'undetermined'
        description = 'Your heart rate is outside the typical resting ranges for dosha analysis. Please ensure you are fully rested and try again.'
        recs = ['Consult a professional for a detailed analysis.']
        
    return {'dosha': dosha, 'description': description, 'recommendations': recs, 'heart_rate': int(heart_rate)}


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames_advanced(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_measurement', methods=['POST'])
def start_measurement_advanced():
    """Starts the PPG measurement process."""
    global measurement_active, green_values, red_values, blue_values, timestamps, liveness_check_passed
    measurement_active = True
    liveness_check_passed = False
    green_values, red_values, blue_values, timestamps = [], [], [], []
    print("Advanced measurement started.")
    return jsonify({'status': 'success', 'message': 'Measurement started.'})

@app.route('/stop_measurement', methods=['POST'])
def stop_measurement_advanced():
    """Stops the measurement and processes the collected PPG data."""
    global measurement_active
    measurement_active = False
    print(f"Measurement stopped. Collected {len(green_values)} data points.")

    if len(green_values) < 60: # Need at least ~2 seconds of data
        message = "Could not get a clear reading. Please ensure your face is well-lit and stable."
        session['ppg_results'] = {'error': message}
        session.modified = True
        return jsonify({'status': 'error', 'message': message})

    fs_est = 1.0 / np.mean(np.diff(timestamps)) if len(timestamps) > 1 else 30
    
    # Use the green channel as it typically has the strongest PPG signal
    heart_rate = calculate_heart_rate_advanced(np.array(green_values), fs_est)

    if heart_rate == 0:
        message = "Heart rate calculation failed. Try again in a brighter, more stable environment."
        session['ppg_results'] = {'error': message}
        session.modified = True
        return jsonify({'status': 'error', 'message': message})

    # Get the detailed Ayurvedic analysis
    ayurvedic_results = analyze_ayurvedic_profile(heart_rate)
    
    # Store results in session for other parts of the app to use
    session['ppg_results'] = ayurvedic_results
    session.modified = True
    print(f"Processing complete. Heart Rate: {ayurvedic_results['heart_rate']} BPM, Dosha: {ayurvedic_results['dosha']}")

    return jsonify({'status': 'success', **ayurvedic_results})


if __name__ == '__main__':
    app.run(debug=True, port=5000)