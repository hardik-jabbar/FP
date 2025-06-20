// assets/js/marketplace-search.js
import { supabase } from './supabase.js';

export class MarketplaceSearch {
  constructor(options = {}) {
    this.container = options.container || document;
    this.filters = {
      category: null,
      minPrice: null,
      maxPrice: null,
      condition: null,
      searchQuery: '',
      ...options.defaultFilters
    };
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.updateResults();
  }

  setupEventListeners() {
    // Category filter
    this.container.addEventListener('change', (e) => {
      if (e.target.matches('[data-filter="category"]')) {
        this.filters.category = e.target.value || null;
        this.updateResults();
      }
    });

    // Price range filter
    ['minPrice', 'maxPrice'].forEach(type => {
      this.container.addEventListener('change', (e) => {
        if (e.target.matches(`[data-filter="${type}"]`)) {
          const value = e.target.value ? parseInt(e.target.value) : null;
          this.filters[type] = value;
          this.updateResults();
        }
      });
    });

    // Search input
    this.container.addEventListener('input', (e) => {
      if (e.target.matches('[data-filter="search"]')) {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
          this.filters.searchQuery = e.target.value.trim();
          this.updateResults();
        }, 300);
      }
    });
  }

  async updateResults() {
    try {
      let query = supabase
        .from('products')
        .select('*')
        .eq('is_active', true);

      // Apply filters
      if (this.filters.category) {
        query = query.eq('category_id', this.filters.category);
      }

      if (this.filters.minPrice) {
        query = query.gte('price_cents', this.filters.minPrice * 100);
      }

      if (this.filters.maxPrice) {
        query = query.lte('price_cents', this.filters.maxPrice * 100);
      }

      if (this.filters.searchQuery) {
        query = query.or(`title.ilike.%${this.filters.searchQuery}%,description.ilike.%${this.filters.searchQuery}%`);
      }

      const { data, error } = await query;
      
      if (error) throw error;
      
      this.renderResults(data);
    } catch (error) {
      console.error('Error updating search results:', error);
    }
  }

  renderResults(products) {
    const grid = this.container.querySelector('[data-results-grid]');
    if (!grid) return;
    
    grid.innerHTML = products.map(product => this.productCard(product)).join('');
  }

  productCard(product) {
    const price = (product.price_cents / 100).toLocaleString(undefined, { 
      style: 'currency', 
      currency: 'USD' 
    });
    
    return `
      <div class="card-hover bg-dark-200 rounded-lg overflow-hidden animate-fade-in" data-id="${product.id}">
        <img src="${product.image_url || 'https://source.unsplash.com/600x400?tractor'}" 
             alt="${product.title}" 
             class="w-full h-48 object-cover">
        <div class="p-4 flex flex-col h-full">
          <h3 class="text-lg font-semibold mb-2">${product.title}</h3>
          <p class="text-gray-400 flex-grow">${product.description || ''}</p>
          <div class="mt-4 flex items-center justify-between">
            <span class="text-xl font-bold">${price}</span>
            <button class="add-to-cart px-3 py-1 bg-primary text-white rounded-md hover:bg-primary/90" 
                    data-product-id="${product.id}">
              Add to Cart
            </button>
          </div>
        </div>
      </div>
    `;
  }
}
