// Cart handler for adding boards to cart
class CartHandler {
    constructor() {
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.updateCartBadge();
    }
    
    bindEvents() {
        // Add to cart button clicks
        document.addEventListener('click', (e) => {
            if (e.target.closest('.add-to-cart-btn')) {
                const btn = e.target.closest('.add-to-cart-btn');
                const boardId = btn.dataset.boardId;
                this.handleAddToCart(boardId, btn);
            }
        });
    }
    
    async handleAddToCart(boardId, btn) {
        try {
            // Disable button to prevent double-clicks
            if (btn) {
                btn.disabled = true;
                const originalHTML = btn.innerHTML;
                btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Adding...';
                
                const response = await fetch(`/cart/add/${boardId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (!response.ok || !data.success) {
                    throw new Error(data.error || 'Failed to add to cart');
                }
                
                // Success!
                if (typeof showToast === 'function') {
                    showToast('🎉 Board added to cart!', 'success');
                }
                
                // Update cart badge
                this.updateCartBadge(data.cart_count);
                
                // Update button to show "In Cart" and keep it disabled
                btn.disabled = true;
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-outline-success');
                btn.innerHTML = '<i class="bi bi-check-circle"></i> In Cart';
                btn.style.cursor = 'not-allowed';
                
            }
            } catch (error) {
                console.error('Add to cart error:', error);
                
                // Re-enable button
                if (btn) {
                    btn.disabled = false;
                    btn.innerHTML = '<i class="bi bi-cart-plus"></i> Add to Cart';
                }
                
                // Show error message above the button
                const errorDiv = document.getElementById(`error-${boardId}`);
                const errorText = document.getElementById(`error-text-${boardId}`);
                if (errorDiv && errorText) {
                    errorText.textContent = error.message || 'Failed to add to cart';
                    errorDiv.style.display = 'block';
                    
                    // Auto-hide after 10 seconds
                    setTimeout(() => {
                        errorDiv.style.display = 'none';
                    }, 10000);
                }
                
                // Also show toast for non-location errors
                if (typeof showToast === 'function' && !error.message.includes('location')) {
                    const errorMsg = error.message.includes('not available') || error.message.includes('already checked out')
                        ? 'Someone beat you to it! But don\'t worry, there are more boards in the sea. 🌊'
                        : `Failed to add to cart: ${error.message}`;
                    showToast(errorMsg, 'error');
                }
            }
    }
    
    async updateCartBadge(count) {
        // Update cart badge in header - only show the number, no icons
        const cartBadge = document.getElementById('headerCartBadge');
        if (cartBadge) {
            if (count !== undefined && count > 0) {
                cartBadge.textContent = count.toString();
                cartBadge.innerHTML = count.toString(); // Ensure no HTML/icons
                cartBadge.style.display = 'inline-block';
            } else if (count === 0) {
                cartBadge.style.display = 'none';
            }
        }
        
        // Also update cart badge in dropdown menu if it exists
        const dropdownCartBadge = document.getElementById('cartBadge');
        if (dropdownCartBadge) {
            if (count !== undefined && count > 0) {
                dropdownCartBadge.textContent = count.toString();
                dropdownCartBadge.innerHTML = count.toString(); // Ensure no HTML/icons
                dropdownCartBadge.style.display = 'inline';
            } else {
                dropdownCartBadge.style.display = 'none';
            }
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.cartHandler = new CartHandler();
});
