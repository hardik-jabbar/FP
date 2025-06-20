// assets/js/favorites.js
import { supabase, getCurrentUser } from './supabase.js';

export class FavoritesManager {
  constructor() {
    this.favorites = new Set();
    this.userId = null;
    this.initialize();
  }

  async initialize() {
    const user = await getCurrentUser();
    if (user) {
      this.userId = user.id;
      await this.loadFavorites();
    }
    this.setupAuthListener();
  }

  setupAuthListener() {
    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (event === 'SIGNED_IN' && session?.user) {
          this.userId = session.user.id;
          await this.loadFavorites();
        } else if (event === 'SIGNED_OUT') {
          this.userId = null;
          this.favorites.clear();
          this.updateUI();
        }
      }
    );

    // Cleanup on destroy
    return () => subscription.unsubscribe();
  }

  async loadFavorites() {
    if (!this.userId) return;

    try {
      const { data, error } = await supabase
        .from('favorites')
        .select('product_id')
        .eq('user_id', this.userId);

      if (error) throw error;

      this.favorites = new Set(data.map(item => item.product_id));
      this.updateUI();
    } catch (error) {
      console.error('Error loading favorites:', error);
    }
  }

  async toggleFavorite(productId) {
    if (!this.userId) {
      // Redirect to login or show login modal
      window.dispatchEvent(new CustomEvent('show-login', { 
        detail: { message: 'Please sign in to save favorites' } 
      }));
      return false;
    }

    try {
      const isFavorite = this.isFavorite(productId);
      
      if (isFavorite) {
        await this.removeFavorite(productId);
      } else {
        await this.addFavorite(productId);
      }

      this.updateUI();
      return !isFavorite;
    } catch (error) {
      console.error('Error toggling favorite:', error);
      return false;
    }
  }

  async addFavorite(productId) {
    if (!this.userId) return false;

    try {
      const { error } = await supabase
        .from('favorites')
        .upsert({
          user_id: this.userId,
          product_id: productId,
          created_at: new Date().toISOString()
        });

      if (error) throw error;
      
      this.favorites.add(productId);
      return true;
    } catch (error) {
      console.error('Error adding favorite:', error);
      throw error;
    }
  }

  async removeFavorite(productId) {
    if (!this.userId) return false;

    try {
      const { error } = await supabase
        .from('favorites')
        .delete()
        .eq('user_id', this.userId)
        .eq('product_id', productId);

      if (error) throw error;
      
      this.favorites.delete(productId);
      return true;
    } catch (error) {
      console.error('Error removing favorite:', error);
      throw error;
    }
  }

  isFavorite(productId) {
    return this.favorites.has(productId);
  }

  async getFavorites() {
    if (!this.userId) return [];
    
    try {
      const { data, error } = await supabase
        .from('favorites')
        .select(`
          product:products (
            id,
            title,
            description,
            price_cents,
            image_url
          )`)
        .eq('user_id', this.userId);

      if (error) throw error;
      
      return data.map(item => ({
        ...item.product,
        is_favorite: true
      }));
    } catch (error) {
      console.error('Error getting favorites:', error);
      return [];
    }
  }

  updateUI() {
    // Dispatch event that favorites were updated
    window.dispatchEvent(new CustomEvent('favorites-updated', { 
      detail: { favorites: Array.from(this.favorites) } 
    }));

    // Update all favorite buttons in the DOM
    document.querySelectorAll('[data-favorite]').forEach(button => {
      const productId = button.dataset.favorite;
      const isFavorite = this.isFavorite(productId);
      
      // Update button appearance
      const icon = button.querySelector('svg');
      if (icon) {
        icon.classList.toggle('fill-current text-red-500', isFavorite);
        icon.classList.toggle('text-gray-400', !isFavorite);
      }
      
      // Update tooltip/aria-label
      const label = isFavorite ? 'Remove from favorites' : 'Add to favorites';
      button.setAttribute('aria-label', label);
      button.title = label;
    });
  }
}

// Initialize a global instance
export const favoritesManager = new FavoritesManager();

// Helper function to create a favorite button
export function createFavoriteButton(productId) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'favorite-button p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors';
  button.dataset.favorite = productId;
  button.setAttribute('aria-label', 'Add to favorites');
  button.title = 'Add to favorites';
  
  button.innerHTML = `
    <svg class="w-6 h-6 text-gray-400 hover:text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
    </svg>
  `;
  
  button.addEventListener('click', async (e) => {
    e.preventDefault();
    e.stopPropagation();
    await favoritesManager.toggleFavorite(productId);
  });
  
  return button;
}
