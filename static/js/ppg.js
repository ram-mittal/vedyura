document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const $startBtn = document.getElementById('start-btn');
    const $stopBtn = document.getElementById('stop-btn');
    const $cameraFeed = document.getElementById('camera-feed');

    // Measurement state
    let isMeasuring = false;

    // Start measurement
    if ($startBtn) {
        $startBtn.addEventListener('click', function() {
            if (isMeasuring) return;
            
            // Show loading state
            $startBtn.disabled = true;
            $startBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Starting...';
            
            // Add pulsing effect to camera feed
            if($cameraFeed) $cameraFeed.classList.add('measurement-active');
            
            // Start measurement on the server
            fetch('/start_measurement', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        isMeasuring = true;
                        $startBtn.disabled = true;
                        $stopBtn.disabled = false;
                        $startBtn.textContent = 'Measuring...';
                    } else {
                        alert('Error: ' + data.message);
                        resetUI();
                    }
                })
                .catch(error => {
                    console.error('Error starting measurement:', error);
                    alert('Failed to start measurement. Please try again.');
                    resetUI();
                });
        });
    }
    
    // Stop measurement button handler
    if ($stopBtn) {
        $stopBtn.addEventListener('click', stopMeasurement);
    }
    
    // Stop the current measurement
    function stopMeasurement() {
        if (!isMeasuring) return;
        
        // Disable buttons and show loading state
        $stopBtn.disabled = true;
        $stopBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
        
        fetch('/stop_measurement', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // SUCCESS! Trigger the event for the main workflow
                    document.dispatchEvent(new CustomEvent('measurementComplete'));
                } else {
                    alert('Error: ' + data.message);
                }
                resetUI();
            })
            .catch(error => {
                console.error('Error stopping measurement:', error);
                alert('Failed to process measurement. Please try again.');
                resetUI();
            });
    }
    
    // Reset UI to initial state
    function resetUI() {
        isMeasuring = false;
        if($startBtn) {
            $startBtn.disabled = false;
            $startBtn.textContent = 'Start Measurement';
        }
        if($stopBtn) {
            $stopBtn.disabled = true;
            $stopBtn.textContent = 'Stop Measurement';
        }
        if($cameraFeed) $cameraFeed.classList.remove('measurement-active');
    }
});
