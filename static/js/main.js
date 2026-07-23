// Main JavaScript for LMS Platform

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        });
    }, 5000);
    
    // Handle course enrollment buttons
    document.querySelectorAll('.enroll-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const courseId = this.dataset.courseId;
            // AJAX enrollment would go here
            alert('Enrollment feature coming soon!');
        });
    });
});