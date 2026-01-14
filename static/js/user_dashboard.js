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
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    if (window.socketClient) {
        window.userDashboard = new UserDashboard(window.socketClient);
    }
});
