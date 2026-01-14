// SocketIO Client for real-time updates
class SocketIOClient {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.messageQueue = [];
        this.init();
    }
    
    init() {
        this.connect();
        this.setupEventHandlers();
    }
    
    connect() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            this.connected = true;
            this.updateConnectionIndicator('connected');
            this.flushMessageQueue();
            console.log('WebSocket connected');
        });
        
        this.socket.on('disconnect', () => {
            this.connected = false;
            this.updateConnectionIndicator('disconnected');
            console.log('WebSocket disconnected');
        });
        
        this.socket.on('reconnect', () => {
            this.connected = true;
            this.updateConnectionIndicator('connected');
            console.log('WebSocket reconnected');
        });
        
        // Listen for board status changes
        this.socket.on('board_status_changed', (data) => {
            this.handleBoardStatusChange(data);
        });
        
        // Listen for notifications
        this.socket.on('notification', (data) => {
            this.handleNotification(data);
        });
    }
    
    subscribeToLocation(locationId) {
        if (this.connected) {
            this.socket.emit('subscribe_location', { location_id: locationId });
        } else {
            this.messageQueue.push({ event: 'subscribe_location', data: { location_id: locationId } });
        }
    }
    
    emit(event, data) {
        if (this.connected) {
            this.socket.emit(event, data);
        } else {
            this.messageQueue.push({ event, data });
        }
    }
    
    flushMessageQueue() {
        while (this.messageQueue.length > 0) {
            const { event, data } = this.messageQueue.shift();
            this.socket.emit(event, data);
        }
    }
    
    updateConnectionIndicator(status) {
        const indicator = document.getElementById('connectionIndicator');
        if (indicator) {
            indicator.className = `connection-indicator ${status}`;
            const badge = indicator.querySelector('.badge');
            if (badge) {
                // Only show indicator when disconnected
                if (status === 'disconnected') {
                    indicator.style.display = 'block';
                    badge.innerHTML = '<i class="bi bi-wifi-off"></i> Disconnected';
                } else {
                    // Hide when connected
                    indicator.style.display = 'none';
                }
            }
        }
    }
    
    handleBoardStatusChange(data) {
        // Update board card in UI
        const boardCard = document.querySelector(`[data-board-id="${data.board_id}"]`);
        if (boardCard) {
            boardCard.dataset.status = data.status;
            boardCard.classList.add('status-transition');
            setTimeout(() => {
                boardCard.classList.remove('status-transition');
            }, 500);
        }
    }
    
    handleNotification(data) {
        if (typeof showToast === 'function') {
            showToast(data.message, data.type || 'info');
        }
    }
}
