import json
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from Prakriti_Bot import get_response 

# --- Vedyura Core Imports ---
from health_analyzer import analyze_user_data, get_llm_diet_chart
from fpdf import FPDF

# --- PPG Integration Imports ---
import cv2
import numpy as np
import time
import base64
from io import BytesIO
import scipy.signal 
from scipy.fft import fft, fftfreq
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend
import matplotlib.pyplot as plt
# --- End PPG Integration Imports ---


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
            data = json.load(f)
            if isinstance(data, dict) and 'requests' in data:
                return data
            return {'requests': []} 
    except (FileNotFoundError, json.JSONDecodeError):
        return {'requests': []}

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

# --- Chatbot API Route ---

@app.route('/predict', methods=['POST'])
def predict():
    """Handles incoming chat messages and returns the bot's response."""
    text = request.get_json().get("message")
    user_id = session.get('user_id', 'anonymous_user') 
    response = get_response(user_id, text)
    message = {"answer": response}
    return jsonify(message)

# --- Doctor Authentication and Dashboard Routes ---

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
        all_requests_data = load_requests()
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
    session['user_id'] = 'bypassed_user'
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


# --- "Rogi Pariksha" Workflow and Diet Chart Generation ---

@app.route('/patient/save-form-data', methods=['POST'])
def save_form_data():
    """Saves the detailed diagnosis form data to the session."""
    if 'user_id' in session and session.get('role') == 'patient':
        session['diagnosis_form_data'] = request.form.to_dict()
        session.modified = True # Ensure the session is saved
        return jsonify({'status': 'success', 'message': 'Form data saved.'})
    return jsonify({'status': 'error', 'message': 'User not authenticated.'})


@app.route('/patient/generate-diet-chart')
def generate_diet_chart():
    """Generates the diet chart PDF and sends it for download."""
    if 'user_id' in session and session.get('role') == 'patient':
        form_data = session.get('diagnosis_form_data', {})
        ppg_data = session.get('ppg_scan_data', {})

        if not form_data:
            return "Error: No form data found. Please complete the form first.", 400

        # 1. Analyze data with the Rule-Based Engine
        health_profile = analyze_user_data(form_data, ppg_data)

        # 2. Get the diet chart text from the (simulated) LLM
        diet_chart_text = get_llm_diet_chart(health_profile)
        
        # 3. Generate the PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=diet_chart_text.encode('latin-1', 'replace').decode('latin-1'))
        
        # 4. Create a response to send the PDF for download
        pdf_output = pdf.output(dest='S').encode('latin-1')
        response = Response(pdf_output)
        response.headers.set('Content-Disposition', 'attachment', filename='Vedyura_Diet_Chart.pdf')
        response.headers.set('Content-Type', 'application/pdf')
        
        return response

    return redirect(url_for('signup'))


# --- PPG Integration Backend Logic ---

# Global variables for signal processing
green_values = []
timestamps = []
fs = 30  # Sampling frequency (frames per second)
start_time = time.time()
measurement_active = False

# Liveness detection variables
liveness_check_active = False
liveness_check_passed = False
blink_detected = False
blink_start_time = 0
blink_duration = 0

# Initialize face and eye cascade classifiers
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')


def bandpass_filter(signal, lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = scipy.signal.butter(order, [low, high], btype='band')
    return scipy.signal.filtfilt(b, a, signal)

def detect_liveness(face_roi):
    global blink_detected, blink_start_time, blink_duration
    try:
        if face_roi.size == 0: return False
        eyes = eye_cascade.detectMultiScale(face_roi)
        if len(eyes) < 2:
            if not blink_detected:
                blink_detected = True
                blink_start_time = time.time()
            else:
                blink_duration = time.time() - blink_start_time
                if 0.1 < blink_duration < 2.0: return True
            return False
        if blink_detected: blink_detected = False
    except Exception as e:
        print(f"Error in detect_liveness: {e}")
    return False

def process_frame(frame):
    global liveness_check_active, liveness_check_passed, green_values, timestamps
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    for (x, y, w, h) in faces:
        color = (0, 255, 0) if liveness_check_passed else (0, 0, 255)
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        
        if measurement_active:
            if not liveness_check_passed and liveness_check_active:
                face_roi = gray[y:y+h, x:x+w]
                if face_roi.size > 0 and detect_liveness(face_roi):
                    liveness_check_passed = True
                    liveness_check_active = False
            
            if liveness_check_passed:
                roi = frame[y:y+h//2, x:x+w]
                if roi.size > 0:
                    g = cv2.split(roi)[1]
                    green_mean = np.mean(g)
                    green_values.append(green_mean)
                    timestamps.append(time.time() - start_time)
    return frame

def calculate_heart_rate(signal, fs):
    if len(signal) < 10: return 0
    signal = signal - np.mean(signal)
    n = len(signal)
    yf = fft(signal)
    xf = fftfreq(n, 1/fs)[:n//2]
    mask = (xf > 0.75) & (xf < 4.0)
    if not any(mask): return 0
    idx = np.argmax(np.abs(yf[:n//2][mask]))
    return xf[mask][idx] * 60

def analyze_ayurvedic(heart_rate):
    if heart_rate < 65: dosha = 'kapha'
    elif heart_rate < 85: dosha = 'vata'
    else: dosha = 'pitta'
    return {'dosha': dosha}

def generate_frames():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return
    while True:
        success, frame = cap.read()
        if not success: break
        frame = process_frame(frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def reset_measurement_state():
    global measurement_active, start_time, green_values, timestamps, liveness_check_active, liveness_check_passed, blink_detected, blink_start_time
    green_values, timestamps = [], []
    start_time = time.time()
    liveness_check_active = True
    liveness_check_passed = False
    blink_detected = False
    blink_start_time = 0
    measurement_active = True

@app.route('/start_measurement', methods=['POST'])
def start_measurement():
    reset_measurement_state()
    return jsonify({'status': 'success', 'message': 'Measurement started.'})

def process_measurement_data():
    global green_values, timestamps
    if len(green_values) < 10:
        return {'status': 'error', 'message': 'Not enough data collected.'}
    try:
        fs = len(timestamps) / (timestamps[-1] - timestamps[0]) if len(timestamps) > 1 else 10
        filtered_signal = bandpass_filter(np.array(green_values), 0.7, 4.0, fs)
        heart_rate = calculate_heart_rate(filtered_signal, fs)
        ayurvedic_info = analyze_ayurvedic(heart_rate)
        return {'status': 'success', 'heart_rate': heart_rate, **ayurvedic_info}
    except Exception as e:
        return {'status': 'error', 'message': f'Error: {str(e)}'}

@app.route('/stop_measurement', methods=['POST'])
def stop_measurement():
    global measurement_active, liveness_check_active
    measurement_active = False
    liveness_check_active = False
    result = process_measurement_data()
    if result['status'] == 'success':
        session['ppg_scan_data'] = {
            'heart_rate': result.get('heart_rate', 0),
            'dosha': result.get('dosha', 'unknown')
        }
        session.modified = True
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)

