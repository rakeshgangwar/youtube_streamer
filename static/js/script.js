document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const statusText = document.getElementById('status');

    startBtn.addEventListener('click', () => {
        fetch('/start_stream', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    startBtn.disabled = true;
                    stopBtn.disabled = false;
                    statusText.textContent = 'Status: Streaming';
                }
            });
    });

    stopBtn.addEventListener('click', () => {
        fetch('/stop_stream', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    startBtn.disabled = false;
                    stopBtn.disabled = true;
                    statusText.textContent = 'Status: Not streaming';
                }
            });
    });

    // Check status periodically
    setInterval(() => {
        fetch('/status')
            .then(response => response.json())
            .then(data => {
                if (data.streaming) {
                    startBtn.disabled = true;
                    stopBtn.disabled = false;
                    statusText.textContent = 'Status: Streaming';
                } else {
                    startBtn.disabled = false;
                    stopBtn.disabled = true;
                    statusText.textContent = 'Status: Not streaming';
                }
            });
    }, 5000);
});