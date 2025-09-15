// Cart management with Supabase sync
const cart = {
    items: [],
    
    // Initialize cart from localStorage and sync with Supabase
    async init() {
        this.loadFromStorage();
        await this.syncWithSupabase();
        this.updateUI();
    },

    // Load cart from localStorage
    loadFromStorage() {
        const savedCart = localStorage.getItem('cart');
        if (savedCart) {
            this.items = JSON.parse(savedCart);
        }
    },

    // Sync cart with Supabase
    async syncWithSupabase() {
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) return;

        try {
            const { data: cartData, error } = await supabase
                .from('carts')
                .select('items')
                .eq('user_id', user.id)
                .single();

            if (error) throw error;

            if (cartData) {
                // Merge local cart with Supabase cart
                this.items = this.mergeCartItems(this.items, cartData.items);
                this.saveToStorage();
            } else {
                // Create new cart in Supabase
                await this.saveToSupabase();
            }
        } catch (error) {
            console.error('Error syncing cart:', error);
        }
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
            
            await this.saveCart();
            return true;
        } catch (error) {
            console.error('Error adding item to cart:', error);
            return false;
        }
    },

    // Remove item from cart
    async removeItem(tractorId) {
        this.items = this.items.filter(item => item.id !== tractorId);
        await this.saveCart();
    },

    // Update item quantity
    async updateQuantity(tractorId, quantity) {
        if (quantity < 1) {
            await this.removeItem(tractorId);
            return;
        }
        
        const item = this.items.find(item => item.id === tractorId);
        if (item) {
            item.quantity = Math.max(0, quantity);
            if (item.quantity === 0) {
                await this.removeItem(tractorId);
            } else {
                await this.saveCart();
            }
        }
    },

    // Save cart to localStorage and Supabase
    async saveCart() {
        this.saveToStorage();
        await this.saveToSupabase();
        this.updateUI();
    },

    // Save cart to localStorage
    saveToStorage() {
        localStorage.setItem('cart', JSON.stringify(this.items));
    },

    // Save cart to Supabase
    async saveToSupabase() {
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) return;

        try {
            const { error } = await supabase
                .from('carts')
                .upsert({
                    user_id: user.id,
                    items: this.items,
                    updated_at: new Date().toISOString()
                });

            if (error) throw error;
        } catch (error) {
            console.error('Error saving cart to Supabase:', error);
        }
    },

    // Merge local and server cart items
    mergeCartItems(localItems, serverItems) {
        const mergedItems = [...localItems];
        
        serverItems.forEach(serverItem => {
            const localItem = mergedItems.find(item => item.id === serverItem.id);
            if (localItem) {
                localItem.quantity = Math.max(localItem.quantity, serverItem.quantity);
            } else {
                mergedItems.push(serverItem);
            }
        });

        return mergedItems;
    },

    // Get cart total
    getTotal() {
        return this.items.reduce((total, item) => total + (item.price * item.quantity), 0);
    },

    // Get cart items count
    getItemsCount() {
        return this.items.reduce((count, item) => count + item.quantity, 0);
    },

    // Update UI elements
    updateUI() {
        this.updateCartCount();
        this.updateMiniCart();
        
        // Dispatch cart update event
        window.dispatchEvent(new CustomEvent('cartUpdated', {
            detail: { items: this.items, total: this.getTotal() }
        }));
    },

    // Update cart count badge
    updateCartCount() {
        const cartCount = document.getElementById('cartCount');
        if (cartCount) {
            const count = this.getItemsCount();
            cartCount.textContent = count;
            cartCount.style.display = count > 0 ? 'flex' : 'none';
        }
    },

    // Update mini cart dropdown
    updateMiniCart() {
        const miniCart = document.getElementById('miniCart');
        if (!miniCart) return;

        if (this.items.length === 0) {
            miniCart.innerHTML = `
                <div class="p-4 text-center text-gray-400">
                    Your cart is empty
                </div>
            `;
            return;
        }

        miniCart.innerHTML = `
            <div class="p-4 max-h-96 overflow-y-auto">
                ${this.items.map(item => `
                    <div class="flex items-center mb-4 last:mb-0">
                        <img src="${item.image_url}" alt="${item.name}" class="w-16 h-16 object-cover rounded">
                        <div class="ml-4 flex-grow">
                            <h4 class="font-medium">${item.name}</h4>
                            <div class="flex items-center mt-1">
                                <span class="text-sm text-gray-400">${item.quantity} × $${item.price.toLocaleString()}</span>
                            </div>
                        </div>
                        <button onclick="cart.removeItem(${item.id})" class="text-red-500 hover:text-red-400 ml-2">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                            </svg>
                        </button>
                    </div>
                `).join('')}
            </div>
            <div class="border-t border-gray-700 p-4">
                <div class="flex justify-between mb-4">
                    <span>Total:</span>
                    <span class="font-bold">$${this.getTotal().toLocaleString()}</span>
                </div>
                <div class="grid grid-cols-2 gap-2">
                    <a href="cart.html" class="bg-white text-dark px-4 py-2 rounded text-center font-medium hover:bg-gray-100 transition-colors">
                        View Cart
                    </a>
                    <a href="checkout.html" class="bg-primary text-white px-4 py-2 rounded text-center font-medium hover:bg-opacity-90 transition-colors">
                        Checkout
                    </a>
                </div>
            </div>
        `;
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