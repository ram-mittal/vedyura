// Wait for the entire HTML document to be loaded and parsed
document.addEventListener('DOMContentLoaded', function() {

    /**
     * ----------------------------------------
     * Dark Mode Toggle Functionality
     * ----------------------------------------
     */
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const body = document.body;

    const applyTheme = () => {
        const isDarkMode = localStorage.getItem('darkMode') === 'true';
        if (isDarkMode) {
            body.classList.add('dark-mode');
        } else {
            body.classList.remove('dark-mode');
        }
    };

    applyTheme();

    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            body.classList.toggle('dark-mode');
            const isDarkModeEnabled = body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDarkModeEnabled);
        });
    }


    /**
     * ----------------------------------------
     * Sign Up Page Role Selection Logic
     * ----------------------------------------
     */
    const selectDoctorBtn = document.getElementById('doctor-btn');
    const selectPatientBtn = document.getElementById('patient-btn');
    const doctorForm = document.getElementById('doctor-login-form');
    const patientOptions = document.getElementById('patient-login-options');

    if (selectDoctorBtn && selectPatientBtn && doctorForm && patientOptions) {
        
        selectDoctorBtn.addEventListener('click', () => {
            doctorForm.classList.remove('hidden');
            patientOptions.classList.add('hidden');
            selectDoctorBtn.classList.add('active');
            selectPatientBtn.classList.remove('active');
        });

        selectPatientBtn.addEventListener('click', () => {
            patientOptions.classList.remove('hidden');
            doctorForm.classList.add('hidden');
            selectPatientBtn.classList.add('active');
            selectDoctorBtn.classList.remove('active');
        });
    }

    /**
     * ----------------------------------------
     * Self-Diagnosis Page Workflow Logic
     * ----------------------------------------
     */
    const diagnosisFormContainer = document.getElementById('diagnosis-form-container');
    const chartActionsContainer = document.getElementById('chart-actions-container');
    const diagnosisForm = document.getElementById('diagnosis-form');
    const submitPopup = document.getElementById('form-submit-popup');
    const scanMeContainer = document.getElementById('scan-me-container');
    const ppgInterfaceContainer = document.getElementById('ppg-interface-container');
    const scanMeBtn = document.getElementById('scan-me-btn');
    const finalOutputContainer = document.getElementById('final-output-container');
    const editFormBtn = document.getElementById('edit-form-btn');

    if (diagnosisForm) {
        diagnosisForm.addEventListener('submit', (e) => {
            e.preventDefault();

            // Show popup
            if (submitPopup) {
                submitPopup.classList.remove('hidden');
                submitPopup.classList.add('show');
            }
            
            setTimeout(() => {
                // Hide popup after 3 seconds
                if (submitPopup) {
                    submitPopup.classList.remove('show');
                    setTimeout(() => {
                        submitPopup.classList.add('hidden');
                    }, 300); // Wait for fade out transition
                }

                // Hide the form container
                if (diagnosisFormContainer) diagnosisFormContainer.classList.add('hidden');
                
                // Show the next step (Scan Me button)
                if (chartActionsContainer) chartActionsContainer.classList.remove('hidden');
                if (scanMeContainer) scanMeContainer.classList.remove('hidden');
                if (ppgInterfaceContainer) ppgInterfaceContainer.classList.add('hidden');
                if (finalOutputContainer) finalOutputContainer.classList.add('hidden');


            }, 3000); // 3-second delay
        });
    }

    if (scanMeBtn) {
        scanMeBtn.addEventListener('click', () => {
            // Hide the "Scan Me" button and show the PPG camera interface
            if (scanMeContainer) scanMeContainer.classList.add('hidden');
            if (ppgInterfaceContainer) ppgInterfaceContainer.classList.remove('hidden');
        });
    }

    // Listen for the custom event from ppg.js
    document.addEventListener('measurementComplete', function() {
        // Hide the PPG interface and show the final download/edit buttons
        if (chartActionsContainer) chartActionsContainer.classList.add('hidden');
        if (ppgInterfaceContainer) ppgInterfaceContainer.classList.add('hidden');
        if (finalOutputContainer) finalOutputContainer.classList.remove('hidden');
    });

    if (editFormBtn) {
        editFormBtn.addEventListener('click', () => {
            // Hide the final buttons and show the form again to allow re-submission
            if (finalOutputContainer) finalOutputContainer.classList.add('hidden');
            if (diagnosisFormContainer) diagnosisFormContainer.classList.remove('hidden');
        });
    }

});

