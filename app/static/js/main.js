// Main JavaScript for Phishing Email Simulator

document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enable Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Handle campaign tab navigation
    var campaignTabs = document.getElementById('campaignTabs');
    if (campaignTabs) {
        campaignTabs.addEventListener('click', function(event) {
            if (event.target.classList.contains('nav-link')) {
                localStorage.setItem('activeTab', event.target.id);
            }
        });
        
        // Restore active tab on page load
        var activeTab = localStorage.getItem('activeTab');
        if (activeTab) {
            var tab = new bootstrap.Tab(document.getElementById(activeTab));
            tab.show();
        }
    }
    
    // Confirmation for delete actions
    var deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                event.preventDefault();
            }
        });
    });
    
    // Target counter for campaign page
    var targetCounter = document.getElementById('targetCounter');
    if (targetCounter) {
        var targetRows = document.querySelectorAll('#targetTable tbody tr');
        targetCounter.textContent = targetRows.length;
    }
    
    // File input preview for CSV imports
    var csvFileInput = document.getElementById('csv_file');
    if (csvFileInput) {
        csvFileInput.addEventListener('change', function(event) {
            var fileName = event.target.files[0].name;
            var fileLabel = document.querySelector('.custom-file-label');
            if (fileLabel) {
                fileLabel.textContent = fileName;
            }
        });
    }
    
    // Campaign status updates
    function updateCampaignStatus() {
        var statusElements = document.querySelectorAll('.campaign-status');
        statusElements.forEach(function(element) {
            var status = element.dataset.status;
            var scheduledTime = element.dataset.scheduledTime;
            
            if (status === 'scheduled' && scheduledTime) {
                var scheduledDate = new Date(scheduledTime);
                var now = new Date();
                
                if (now > scheduledDate) {
                    element.innerHTML = '<span class="badge bg-warning">In Progress</span>';
                }
            }
        });
    }
    
    // Run status updates if elements exist
    if (document.querySelector('.campaign-status')) {
        updateCampaignStatus();
        setInterval(updateCampaignStatus, 60000); // Check every minute
    }
});
