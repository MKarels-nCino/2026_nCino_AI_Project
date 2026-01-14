// Main application initialization
document.addEventListener('DOMContentLoaded', function() {
    console.log('Surfboard Checkout System initialized');
    
    // Initialize SocketIO client if user is authenticated
    if (typeof io !== 'undefined') {
        window.socketClient = new SocketIOClient();
    }
    
    // Initialize toast notifications
    initializeToasts();
});

// Toast notification system
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: type === 'error' ? 4000 : 2500  // Shorter delays, auto-dismiss
    });
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}

function initializeToasts() {
    // Don't convert flash messages to toasts - let them display normally
    // Flash messages are already styled and dismissible in the template
    // Only use toasts for real-time notifications from Socket.IO
}
