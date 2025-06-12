// Cart management
const cart = {
    items: [],
    
    // Initialize cart from localStorage
    init() {
        const savedCart = localStorage.getItem('cart');
        if (savedCart) {
            this.items = JSON.parse(savedCart);
        }
        this.updateCartCount();
    },

    // Add item to cart
    async addItem(tractorId) {
        try {
            const tractor = await api.getTractor(tractorId);
            const existingItem = this.items.find(item => item.id === tractorId);
            
            if (existingItem) {
                existingItem.quantity += 1;
            } else {
                this.items.push({
                    id: tractor.id,
                    name: tractor.name,
                    price: tractor.price,
                    image_url: tractor.image_url,
                    quantity: 1
                });
            }
            
            this.saveCart();
            this.updateCartCount();
            return true;
        } catch (error) {
            console.error('Error adding item to cart:', error);
            return false;
        }
    },

    // Remove item from cart
    removeItem(tractorId) {
        this.items = this.items.filter(item => item.id !== tractorId);
        this.saveCart();
        this.updateCartCount();
    },

    // Update item quantity
    updateQuantity(tractorId, quantity) {
        const item = this.items.find(item => item.id === tractorId);
        if (item) {
            item.quantity = Math.max(0, quantity);
            if (item.quantity === 0) {
                this.removeItem(tractorId);
            } else {
                this.saveCart();
                this.updateCartCount();
            }
        }
    },

    // Get cart total
    getTotal() {
        return this.items.reduce((total, item) => total + (item.price * item.quantity), 0);
    },

    // Save cart to localStorage
    saveCart() {
        localStorage.setItem('cart', JSON.stringify(this.items));
    },

    // Update cart count in header
    updateCartCount() {
        const count = this.items.reduce((total, item) => total + item.quantity, 0);
        const cartCount = document.getElementById('cartCount');
        if (cartCount) {
            cartCount.textContent = count;
            cartCount.style.display = count > 0 ? 'block' : 'none';
        }
    },

    // Clear cart
    clearCart() {
        this.items = [];
        this.saveCart();
        this.updateCartCount();
    }
};

// Initialize cart when script loads
cart.init();

// Export cart to window object
window.cart = cart; 