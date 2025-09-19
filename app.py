import json
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response, make_response

# --- NEW: Import the Personal Diet Tool ---
from personal_diet_tool import get_tool_response

# --- NEW: Import for PDF Generation ---
from fpdf import FPDF

# --- NEW: Import the Health Analyzer ---
from health_analyzer import generate_health_profile, determine_dominant_dosha

# --- Imports for PPG Functionality ---
import cv2
import numpy as np
import time
from scipy import signal

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

    # UPDATED: Use the new Personal Diet Tool
    user_session_data = {
        'form_data': session.get('form_data'),
        'ppg_results': session.get('ppg_results')
    }
    response = get_tool_response(user_id, text, user_session_data)

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

# --- "Rogi Pariksha" and Recipe Workflow Routes ---

@app.route('/patient/save-form-data', methods=['POST'])
def save_form_data():
    """Saves the detailed form data and determined dosha to the user's session."""
    if 'user_id' in session and session.get('role') == 'patient':
        form_data = request.form.to_dict()
        session['form_data'] = form_data

        # Analyze and store the dominant dosha immediately
        session['dominant_dosha'] = determine_dominant_dosha(form_data)

        session.modified = True
        return jsonify({'status': 'success', 'message': 'Form data saved.'})
    return jsonify({'status': 'error', 'message': 'User not logged in.'})


# --- MODIFIED: PDF Generation Route with table fix and new metrics ---
@app.route('/patient/generate-diet-chart')
def generate_diet_chart_pdf():
    """Generates and returns a well-formatted diet chart as a downloadable PDF."""
    if 'user_id' not in session or session.get('role') != 'patient':
        return redirect(url_for('signup'))

    form_data = session.get('form_data')
    ppg_results = session.get('ppg_results', {})

    if not form_data:
        return "Error: No form data found. Please complete the self-diagnosis form first.", 400

    plan_type = request.args.get('plan_type', 'daily')
    health_profile = generate_health_profile(form_data, ppg_results, plan_type)

    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 16)
            self.set_text_color(34, 139, 34) # Forest Green
            self.cell(0, 10, 'Vedyura Personalized Health Plan', 0, 1, 'C')
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

        def section_title(self, title):
            self.set_font('Arial', 'B', 12)
            self.set_fill_color(200, 220, 200) # Light Green
            self.set_text_color(0, 0, 0)
            self.cell(0, 8, title, 0, 1, 'L', fill=True)
            self.ln(4)

        def section_body(self, body):
            body = body.encode('latin-1', 'replace').decode('latin-1')
            self.set_font('Arial', '', 11)
            self.set_text_color(0, 0, 0)
            self.multi_cell(0, 6, body)
            self.ln()

        # --- NEW: Heavily revised table creation method to fix all overlap issues ---
        def create_table(self, table_data, headers, col_widths):
            self.set_font('Arial', 'B', 10)
            self.set_fill_color(230, 230, 230)
            # Header
            for i, header in enumerate(headers):
                self.cell(col_widths[i], 7, header, 1, 0, 'C', 1)
            self.ln()

            # Data rows
            self.set_font('Arial', '', 10)
            line_height = self.font_size * 1.5

            for row in table_data:
                start_y = self.get_y()
                x_pos = self.get_x()
                max_y = start_y

                # Draw the cells and track the maximum Y position
                for i, header in enumerate(headers):
                    key = header.lower().replace(' ', '_')
                    text = str(row.get(key, '')).encode('latin-1', 'replace').decode('latin-1')
                    self.set_xy(x_pos, start_y)
                    self.multi_cell(col_widths[i], line_height, text, 0, 'L')
                    # Update max_y if the current cell is taller
                    if self.get_y() > max_y:
                        max_y = self.get_y()
                    x_pos += col_widths[i]

                # Draw borders for the entire row using the calculated max height
                self.set_xy(self.l_margin, start_y) # Go back to the start of the row
                row_height = max_y - start_y
                for i, _ in enumerate(headers):
                    self.cell(col_widths[i], row_height, '', 1, 0)

                # Move cursor to the bottom of the drawn row for the next iteration
                self.set_y(max_y)


    pdf = PDF()
    pdf.add_page()

    # 1. Profile Summary
    pdf.section_title('Your Health Profile Summary')
    pdf.section_body(health_profile['profile_summary'])

    # 2. Key Health Metrics Section
    pdf.section_title('Key Health Metrics')
    bmi_val = health_profile.get('bmi_value') or "N/A"
    bmi_cat = health_profile.get('bmi_category') or "Not Calculated"
    hr_val = int(health_profile.get('heart_rate')) if health_profile.get('heart_rate') else "N/A"
    protein_val = health_profile.get('protein_target') or "Not Calculated"

    metrics_text = (
        f"Body Mass Index (BMI): {bmi_val} ({bmi_cat})\n"
        f"Resting Heart Rate: {hr_val} BPM\n"
        f"Estimated Daily Protein Intake: {protein_val}"
    )
    pdf.section_body(metrics_text)

    # 3. Meal Plan
    plan_title = 'Your Daily Meal Plan'
    if health_profile['plan_type'] == 'weekly':
        plan_title = 'Your Weekly Meal Plan'

    pdf.section_title(f"{plan_title} (Approx. Target: {health_profile['calories']} kcal per day)")

    if health_profile['plan_type'] == 'weekly':
        table_headers = ['Day', 'Meal', 'Food', 'Rationale']
        col_widths = [25, 25, 60, 80]
    else:
        table_headers = ['Meal', 'Food', 'Rationale']
        col_widths = [30, 80, 80]

    pdf.create_table(health_profile['meal_plan'], table_headers, col_widths)
    pdf.ln(5)

    # 4. Lifestyle Recommendations
    pdf.section_title('Personalized Lifestyle Recommendations')
    pdf.section_body(health_profile['recommendations'])

    # 5. Yoga Sequence
    pdf.section_title('Your Daily Yoga & Movement Sequence')
    yoga_text = health_profile['yoga_sequence'].replace('**', '')
    pdf.section_body(yoga_text)

    # 6. Disclaimer
    pdf.section_title('Disclaimer')
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 5, health_profile['disclaimer'])

    # Create response
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    response = make_response(pdf_bytes)
    response.headers.set('Content-Disposition', 'attachment', filename='Vedyura_Diet_Chart.pdf')
    response.headers.set('Content-Type', 'application/pdf')

    return response


# --- API Route to fetch recipes ---
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


# --- PPG (Heart Rate Monitor) Integration ---

# Global variables
green_values = []
timestamps = []
measurement_active = False
liveness_check_passed = False
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    y = signal.filtfilt(b, a, data)
    return y

def calculate_heart_rate(signal_data, fs):
    if len(signal_data) < fs * 2:
        return 0
    peaks, _ = signal.find_peaks(signal_data, height=0.5 * np.std(signal_data))
    if len(peaks) < 2:
        return 0
    avg_interval = np.mean(np.diff(peaks)) / fs
    heart_rate = 60 / avg_interval
    return heart_rate

def process_frame(frame):
    global green_values, timestamps, liveness_check_passed, measurement_active
    if not measurement_active:
        return frame

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    if not liveness_check_passed:
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            roi_gray = gray[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
            if len(eyes) == 0:
                 liveness_check_passed = True

    if liveness_check_passed:
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            forehead = frame[y+h//10:y+h//4, x+w//4:x+3*w//4]
            if forehead.size > 0:
                green_values.append(np.mean(forehead[:,:,1]))
                timestamps.append(time.time())
    else:
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
    return frame

def generate_frames():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return
    while True:
        success, frame = cap.read()
        if not success:
            break
        frame = process_frame(frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    cap.release()


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_measurement', methods=['POST'])
def start_measurement():
    global measurement_active, green_values, timestamps, liveness_check_passed
    measurement_active = True
    liveness_check_passed = False
    green_values = []
    timestamps = []
    return jsonify({'status': 'success'})

@app.route('/stop_measurement', methods=['POST'])
def stop_measurement():
    global measurement_active
    measurement_active = False

    if len(green_values) < 20:
        message = "Could not get a clear reading. Generating chart based on form answers only."
        session['ppg_results'] = {'error': message}
        session.modified = True
        return jsonify({'status': 'error', 'message': message})

    fs_est = 1.0 / np.mean(np.diff(timestamps))
    filtered_signal = bandpass_filter(green_values, 0.8, 2.5, fs_est)
    heart_rate = calculate_heart_rate(filtered_signal, fs_est)

    if not (40 < heart_rate < 160):
        message = f"Heart rate ({int(heart_rate)} bpm) out of normal range. Generating chart based on form answers only."
        session['ppg_results'] = {'error': message, 'heart_rate': heart_rate}
        session.modified = True
        return jsonify({'status': 'error', 'message': message})

    ppg_results = {'heart_rate': heart_rate}
    session['ppg_results'] = ppg_results
    session.modified = True

    return jsonify({'status': 'success', 'heart_rate': heart_rate})


if __name__ == '__main__':
    app.run(debug=True)