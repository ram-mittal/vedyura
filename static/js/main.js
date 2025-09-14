// Wait for the entire HTML document to be loaded and parsed
document.addEventListener('DOMContentLoaded', function() {

    /**
     * ----------------------------------------
     * Dark Mode Toggle Functionality
     * ----------------------------------------
     */
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const body = document.body;

    // Function to apply the saved theme on page load
    const applyTheme = () => {
        const isDarkMode = localStorage.getItem('darkMode') === 'true';
        if (isDarkMode) {
            body.classList.add('dark-mode');
        } else {
            body.classList.remove('dark-mode');
        }
    };

    // Apply theme as soon as the page loads
    applyTheme();

    // Add click event listener to the toggle button
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            body.classList.toggle('dark-mode');
            // Save the user's preference to localStorage
            const isDarkModeEnabled = body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDarkModeEnabled);
        });
    }


    /**
     * ----------------------------------------
     * Sign Up Page Role Selection Logic
     * ----------------------------------------
     */
    // CORRECTED: The button IDs now match the HTML file (doctor-btn, patient-btn)
    const selectDoctorBtn = document.getElementById('doctor-btn');
    const selectPatientBtn = document.getElementById('patient-btn');
    const doctorForm = document.getElementById('doctor-login-form');
    const patientOptions = document.getElementById('patient-login-options');

    // We only run this code if we are on the signup page (i.e., the buttons exist)
    if (selectDoctorBtn && selectPatientBtn && doctorForm && patientOptions) {
        
        selectDoctorBtn.addEventListener('click', () => {
            // Show doctor form, hide patient options
            doctorForm.classList.remove('hidden');
            patientOptions.classList.add('hidden');
            
            // Set active state for buttons
            selectDoctorBtn.classList.add('active');
            selectPatientBtn.classList.remove('active');
        });

        selectPatientBtn.addEventListener('click', () => {
            // Show patient options, hide doctor form
            patientOptions.classList.remove('hidden');
            doctorForm.classList.add('hidden');

            // Set active state for buttons
            selectPatientBtn.classList.add('active');
            selectDoctorBtn.classList.remove('active');
        });
    }

});
