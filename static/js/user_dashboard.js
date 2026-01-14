// User dashboard functionality
class UserDashboard {
    constructor(socketClient) {
        this.socketClient = socketClient;
        this.init();
    }
    
    init() {
        if (this.socketClient && this.socketClient.connected) {
            // Subscribe to location updates
            const locationId = document.body.dataset.locationId;
            if (locationId) {
                this.socketClient.subscribeToLocation(locationId);
            }
        }
        
        // Handle fulfill reservation buttons
        this.bindFulfillReservation();
    }
    
    bindFulfillReservation() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.fulfill-btn')) {
                const btn = e.target.closest('.fulfill-btn');
                const reservationId = btn.dataset.reservationId;
                this.handleFulfillReservation(reservationId, btn);
            }
        });
    }
    
    async handleFulfillReservation(reservationId, btn) {
        try {
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Processing...';
            }
            
            const response = await fetch(`/api/fulfill-reservation/${reservationId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Failed to fulfill reservation');
            }
            
            // Success!
            if (typeof showToast === 'function') {
                showToast('🎉 Reservation fulfilled! Time to ride!', 'success');
            }
            
            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
            
        } catch (error) {
            console.error('Fulfill reservation error:', error);
            
            // Re-enable button
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '<i class="bi bi-check-circle"></i> Fulfill Reservation';
            }
            
            // Show error message
            if (typeof showToast === 'function') {
                showToast(`Failed to fulfill reservation: ${error.message}`, 'error');
            }
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    if (window.socketClient) {
        window.userDashboard = new UserDashboard(window.socketClient);
    } else {
        window.userDashboard = new UserDashboard(null);
    }
});
