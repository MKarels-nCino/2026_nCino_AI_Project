// Checkout handler for user interactions
class CheckoutHandler {
    constructor(socketClient) {
        this.socketClient = socketClient;
        this.init();
    }
    
    init() {
        this.bindEvents();
    }
    
    bindEvents() {
        // Checkout button clicks
        document.addEventListener('click', (e) => {
            if (e.target.closest('.checkout-btn')) {
                const btn = e.target.closest('.checkout-btn');
                const boardId = btn.dataset.boardId;
                this.handleCheckout(boardId, btn);
            }
            
            if (e.target.closest('.return-btn')) {
                const btn = e.target.closest('.return-btn');
                const checkoutId = btn.dataset.checkoutId;
                this.handleReturn(checkoutId, btn);
            }
        });
    }
    
    async handleCheckout(boardId, btn) {
        try {
            // Disable button to prevent double-clicks
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Checking out...';
            }
            
            // Optimistic UI update
            const boardCard = document.querySelector(`[data-board-id="${boardId}"]`);
            if (boardCard) {
                boardCard.style.opacity = '0.5';
                boardCard.style.pointerEvents = 'none';
            }
            
            const response = await fetch(`/api/checkout/${boardId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Checkout failed');
            }
            
            // Success!
            if (typeof showToast === 'function') {
                showToast('🎉 Board checked out! Time to make some memories (and probably some wipeouts)!', 'success');
            }
            
            // Remove board from available list with animation
            if (boardCard) {
                boardCard.style.transition = 'all 0.3s ease';
                boardCard.style.transform = 'scale(0)';
                setTimeout(() => {
                    boardCard.remove();
                }, 300);
            }
            
            // Reload page to show updated checkouts
            setTimeout(() => {
                window.location.reload();
            }, 500);
        } catch (error) {
            console.error('Checkout error:', error);
            
            // Re-enable button
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '<i class="bi bi-cart-plus"></i> Checkout';
            }
            
            // Show error message
            if (typeof showToast === 'function') {
                const errorMsg = error.message.includes('not available') || error.message.includes('already checked out')
                    ? 'Someone beat you to it! But don\'t worry, there are more boards in the sea. 🌊'
                    : `That checkout wiped out: ${error.message}. Let's try again!`;
                showToast(errorMsg, 'error');
            }
            
            // Revert optimistic update
            const boardCard = document.querySelector(`[data-board-id="${boardId}"]`);
            if (boardCard) {
                boardCard.style.opacity = '1';
                boardCard.style.pointerEvents = 'auto';
            }
        }
    }
    
    async handleReturn(checkoutId) {
        if (!confirm('Return this board? Hope you had fun out there! If it got damaged, you can report it after returning.')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/return/${checkoutId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    has_damage: false
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                if (typeof showToast === 'function') {
                    showToast('🏄 Board returned! Hope you had fun out there!', 'success');
                }
                
                // Reload page
                setTimeout(() => {
                    window.location.reload();
                }, 500);
            } else {
                throw new Error(data.error || 'Return failed');
            }
        } catch (error) {
            console.error('Return error:', error);
            if (typeof showToast === 'function') {
                showToast(`Return hit a snag: ${error.message}. Let's try again!`, 'error');
            }
        }
    }
}

// Initialize on page load - wait for all scripts to load
(function() {
    function initCheckoutHandler() {
        // Wait for socketClient to be available (it's initialized in main.js)
        const socketClient = window.socketClient || null;
        window.checkoutHandler = new CheckoutHandler(socketClient);
        console.log('CheckoutHandler initialized');
    }
    
    // Try to initialize immediately if DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCheckoutHandler);
    } else {
        // DOM already loaded, but wait a bit for other scripts
        setTimeout(initCheckoutHandler, 100);
    }
})();
