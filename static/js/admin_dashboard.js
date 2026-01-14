// Admin dashboard functionality
class AdminDashboard {
    constructor(socketClient) {
        this.socketClient = socketClient;
        this.init();
    }
    
    init() {
        if (this.socketClient && this.socketClient.connected) {
            // Subscribe to location updates for real-time stats
            const locationId = document.body.dataset.locationId;
            if (locationId) {
                this.socketClient.subscribeToLocation(locationId);
            }
        }
        
        // Set up real-time updates for stats
        this.setupRealtimeUpdates();
    }
    
    setupRealtimeUpdates() {
        if (this.socketClient) {
            // Listen for board status changes to update stats
            this.socketClient.socket.on('board_status_changed', (data) => {
                this.updateStats();
            });
            
            this.socketClient.socket.on('checkout_created', (data) => {
                this.updateStats();
            });
            
            this.socketClient.socket.on('checkout_returned', (data) => {
                this.updateStats();
            });
        }
    }
    
    updateStats() {
        // Reload stats cards (could be optimized to update specific values)
        // For now, we'll just show a subtle indicator that data is updating
        const cards = document.querySelectorAll('.card.bg-success, .card.bg-warning, .card.bg-danger, .card.bg-info');
        cards.forEach(card => {
            card.classList.add('pulse');
            setTimeout(() => card.classList.remove('pulse'), 1000);
        });
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    if (window.socketClient) {
        window.adminDashboard = new AdminDashboard(window.socketClient);
    }
});
