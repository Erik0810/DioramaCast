// UI Utilities Module
// Handles UI utility functions like status messages and modals

// Open settings modal
function openSettingsModal() {
    const modal = document.getElementById('settings-modal');
    modal.classList.add('show');
}

// Close settings modal
function closeSettingsModal() {
    const modal = document.getElementById('settings-modal');
    modal.classList.remove('show');
}

// Show status message
function showStatus(message, type) {
    const statusEl = document.getElementById('generation-status');
    statusEl.textContent = message;
    statusEl.className = `status-message show ${type}`;
}

// Hide status message
function hideStatus() {
    const statusEl = document.getElementById('generation-status');
    statusEl.className = 'status-message';
}
