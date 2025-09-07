// Show/hide custom value input based on selection
document.addEventListener('DOMContentLoaded', function() {
    const fillMissingSelect = document.querySelector('select[name="fill_missing"]');
    const customValueContainer = document.getElementById('custom-value-container');
    
    if (fillMissingSelect && customValueContainer) {
        fillMissingSelect.addEventListener('change', function() {
            customValueContainer.style.display = this.value === 'custom' ? 'block' : 'none';
        });
        
        // Initial state
        customValueContainer.style.display = fillMissingSelect.value === 'custom' ? 'block' : 'none';
    }
    
    // File input label update
    const fileInput = document.getElementById('file');
    const fileLabel = document.querySelector('label[for="file"]');
    
    if (fileInput && fileLabel) {
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                fileLabel.textContent = this.files[0].name;
            } else {
                fileLabel.textContent = 'Select file (CSV or Excel)';
            }
        });
    }
});