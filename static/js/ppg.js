$(document).ready(function() {
    // DOM Elements
    const $startBtn = $('#start-btn');
    const $stopBtn = $('#stop-btn');
    const $cameraFeed = $('#camera-feed');

    // Measurement state
    let isMeasuring = false;
    let measurementInterval;
    let measurementStartTime = 0;
    const MEASUREMENT_DURATION = 25000; // 25 seconds for data collection

    // Start measurement
    $startBtn.on('click', function() {
        if (isMeasuring) return;
        
        // Show loading state
        $startBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Starting...');
        
        // Add pulsing effect to camera feed
        $cameraFeed.addClass('measurement-active');
        
        // Start measurement on the server
        $.ajax({
            url: '/start_measurement',
            method: 'POST',
            success: function(response) {
                isMeasuring = true;
                $startBtn.prop('disabled', true);
                $stopBtn.prop('disabled', false);
                
                showInstruction('Please look at the camera and blink your eyes. The scan will run for 25 seconds.');
                
                // Start the timer that will automatically stop the measurement and show countdown
                startPolling();
            },
            error: function() {
                showError('Failed to start measurement. Please try again.');
                resetUI();
            }
        });
    });
    
    // Stop measurement button handler (for manual stop)
    $stopBtn.on('click', stopMeasurement);
    
    // This function now primarily acts as an automatic timeout and countdown timer
    function startPolling() {
        measurementStartTime = Date.now();
        
        clearInterval(measurementInterval);
        
        measurementInterval = setInterval(function() {
            if (!isMeasuring) {
                clearInterval(measurementInterval);
                return;
            }
            
            const elapsed = Date.now() - measurementStartTime;
            const remaining = Math.max(0, MEASUREMENT_DURATION - elapsed);
            
            // --- NEW: Update the button text with remaining time ---
            const seconds = Math.ceil(remaining / 1000);
            $startBtn.html(`Scanning... (${seconds}s)`);
            
            // Auto-stop when time is up
            if (remaining <= 0) {
                stopMeasurement();
            }
        }, 500); // Update countdown every half second
    }
    
    // Function to stop the measurement
    function stopMeasurement() {
        if (!isMeasuring) return;
        
        // Prevent this function from being called multiple times
        isMeasuring = false; 
        clearInterval(measurementInterval);
        
        // Disable buttons and show processing state
        $startBtn.html('Processing...');
        $stopBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
        
        $.ajax({
            url: '/stop_measurement',
            method: 'POST',
            timeout: 10000,
            success: function(response) {
                if (response.status === 'error') {
                    console.warn("PPG Scan Warning:", response.message);
                    showInstruction("Could not get a clear reading, but generating chart based on your form answers.");
                } else {
                     showInstruction("Scan complete! Generating your personalized diet chart...");
                }
            },
            error: function() {
                showError('Failed to process scan data. Please try again.');
            },
            complete: function() {
                // *** CRUCIAL STEP ***
                // Signal to main.js that the measurement process is over, regardless of success or failure.
                document.dispatchEvent(new CustomEvent('measurementComplete'));
                resetUI();
            }
        });
    }
    
    // Reset UI to initial state after everything is done
    function resetUI() {
        $startBtn.prop('disabled', false).text('Start Measurement');
        $stopBtn.prop('disabled', true).text('Stop Measurement');
        $cameraFeed.removeClass('measurement-active');
    }
    
    // Helper function to show a temporary message
    function showInstruction(message) {
        $('.instruction-alert').remove();
        const $instruction = $('<div class="alert alert-info instruction-alert">' + message + '</div>');
        $('body').append($instruction);
        setTimeout(() => $instruction.addClass('show'), 100);
    }
    
    // Helper function to show an error message
    function showError(message) {
        $('.instruction-alert, .error-alert').remove();
        const $error = $('<div class="alert alert-danger error-alert">' + message + '</div>');
        $('body').append($error);
        setTimeout(() => $error.addClass('show'), 100);
        setTimeout(() => {
            $error.removeClass('show');
            setTimeout(() => $error.remove(), 300);
        }, 5000);
    }
});

