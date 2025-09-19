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
     * Self-Diagnosis Page Workflow Logic ("Rogi Pariksha")
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
    
    // NEW: Get references to the two new download buttons
    const downloadDailyChartBtn = document.getElementById('download-daily-chart-btn');
    const downloadWeeklyChartBtn = document.getElementById('download-weekly-chart-btn');
    
    // REMOVED: The old single download button reference is no longer needed.
    // const downloadChartBtn = document.getElementById('download-chart-btn');
    
    const cameraFeed = document.getElementById('camera-feed');

    // --- Camera Control ---
    const stopCamera = () => {
        if (cameraFeed) {
            // Setting src to an invalid value stops the browser's stream.
            cameraFeed.src = '#';
        }
    };
    
    // Stop the camera when the page first loads to prevent it from starting automatically.
    stopCamera();

    if (diagnosisForm) {
        diagnosisForm.addEventListener('submit', (e) => {
            e.preventDefault();

            // --- Save Form Data to Server ---
            const formData = new FormData(diagnosisForm);
            fetch('/patient/save-form-data', {
                method: 'POST',
                body: formData
            }).then(response => response.json())
              .then(data => {
                  if(data.status === 'success') {
                      // --- Show popup ---
                      submitPopup.classList.remove('hidden');
                      submitPopup.classList.add('show');
                      
                      setTimeout(() => {
                          // Hide popup
                          submitPopup.classList.remove('show');
                          setTimeout(() => {
                              submitPopup.classList.add('hidden');
                          }, 300);

                          // Hide form, show "Scan Me" button container
                          diagnosisFormContainer.classList.add('hidden');
                          chartActionsContainer.classList.remove('hidden');
                          scanMeContainer.classList.remove('hidden');
                          ppgInterfaceContainer.classList.add('hidden');
                          finalOutputContainer.classList.add('hidden');

                      }, 1000); 
                  } else {
                      alert('Error saving form data. Please try again.');
                  }
              }).catch(error => {
                  console.error('Error:', error);
                  alert('An error occurred. Please try again.');
              });
        });
    }

    if (scanMeBtn) {
        scanMeBtn.addEventListener('click', () => {
            // Hide "Scan Me" button, show PPG interface
            scanMeContainer.classList.add('hidden');
            ppgInterfaceContainer.classList.remove('hidden');
            
            // Start the camera feed by setting the correct source
            if (cameraFeed) {
                // Add a timestamp to prevent browser caching of the stream URL
                cameraFeed.src = '/video_feed?' + new Date().getTime();
            }
        });
    }

    // This is the crucial listener for the signal from ppg.js
    document.addEventListener('measurementComplete', function() {
        // Hide the PPG container 
        chartActionsContainer.classList.add('hidden');
        // Show the final download/edit buttons
        finalOutputContainer.classList.remove('hidden');
        // Stop the camera feed
        stopCamera();
    });

    if (editFormBtn) {
        editFormBtn.addEventListener('click', () => {
            // Hide final buttons, show the form again to start over
            finalOutputContainer.classList.add('hidden');
            diagnosisFormContainer.classList.remove('hidden');
            // Stop the camera feed
            stopCamera();
        });
    }

    // REMOVED: The old event listener for the single download button.
    // if(downloadChartBtn) {
    //     downloadChartBtn.addEventListener('click', () => {
    //         // Trigger the download from the backend
    //         window.location.href = '/patient/generate-diet-chart';
    //     });
    // }
    
    // NEW: Add event listener for the daily chart button
    if(downloadDailyChartBtn) {
        downloadDailyChartBtn.addEventListener('click', () => {
            // Trigger the download, specifying 'daily' plan type
            window.location.href = '/patient/generate-diet-chart?plan_type=daily';
        });
    }

    // NEW: Add event listener for the weekly chart button
    if(downloadWeeklyChartBtn) {
        downloadWeeklyChartBtn.addEventListener('click', () => {
            // Trigger the download, specifying 'weekly' plan type
            window.location.href = '/patient/generate-diet-chart?plan_type=weekly';
        });
    }
});