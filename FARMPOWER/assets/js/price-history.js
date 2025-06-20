// assets/js/price-history.js
import { supabase } from './supabase.js';

export class PriceHistory {
  constructor() {
    this.priceHistory = new Map();
  }

  // Track price changes for a product
  async trackPriceChange(productId, newPriceCents, userId = null) {
    try {
      // Get current price
      const { data: product, error } = await supabase
        .from('products')
        .select('price_cents')
        .eq('id', productId)
        .single();

      if (error) throw error;
      if (!product) throw new Error('Product not found');

      const currentPrice = product.price_cents;
      
      // If price hasn't changed, don't log
      if (currentPrice === newPriceCents) {
        return { changed: false };
      }

      // Log the price change
      const { data, error: logError } = await supabase
        .from('price_history')
        .insert([{
          product_id: productId,
          previous_price: currentPrice,
          new_price: newPriceCents,
          changed_by: userId
        }])
        .select();

      if (logError) throw logError;

      // Update the cache
      if (!this.priceHistory.has(productId)) {
        this.priceHistory.set(productId, []);
      }
      this.priceHistory.get(productId).unshift({
        ...data[0],
        created_at: new Date().toISOString()
      });

      return { 
        changed: true, 
        previousPrice: currentPrice,
        newPrice: newPriceCents,
        history: data[0]
      };
    } catch (error) {
      console.error('Error tracking price change:', error);
      throw error;
    }
  }

  // Get price history for a product
  async getPriceHistory(productId, limit = 10) {
    try {
      // Check cache first
      if (this.priceHistory.has(productId)) {
        return this.priceHistory.get(productId).slice(0, limit);
      }

      // Fetch from database
      const { data, error } = await supabase
        .from('price_history')
        .select('*')
        .eq('product_id', productId)
        .order('created_at', { ascending: false })
        .limit(limit);

      if (error) throw error;

      // Update cache
      this.priceHistory.set(productId, data);
      
      return data;
    } catch (error) {
      console.error('Error fetching price history:', error);
      throw error;
    }
  }

  // Render price history as HTML
  async renderPriceHistory(container, productId) {
    try {
      const history = await this.getPriceHistory(productId);
      
      if (!history || history.length === 0) {
        container.innerHTML = '<p class="text-gray-500">No price history available.</p>';
        return;
      }

      const html = `
        <div class="space-y-4">
          <h3 class="text-lg font-medium">Price History</h3>
          <div class="space-y-2">
            ${history.map(entry => this.renderHistoryItem(entry)).join('')}
          </div>
        </div>
      `;
      
      container.innerHTML = html;
    } catch (error) {
      console.error('Error rendering price history:', error);
      container.innerHTML = '<p class="text-red-500">Error loading price history.</p>';
    }
  }

  // Helper to format a single history item
  renderHistoryItem(entry) {
    const date = new Date(entry.created_at).toLocaleDateString();
    const oldPrice = (entry.previous_price / 100).toLocaleString('en-US', { 
      style: 'currency', 
      currency: 'USD' 
    });
    const newPrice = (entry.new_price / 100).toLocaleString('en-US', { 
      style: 'currency', 
      currency: 'USD' 
    });
    const change = entry.new_price - entry.previous_price;
    const changePercent = Math.abs(change / entry.previous_price * 100).toFixed(2);
    const isIncrease = change > 0;

    return `
      <div class="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-500">${date}</span>
          <span class="text-xs px-2 py-1 rounded-full ${isIncrease ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'}">
            ${isIncrease ? '↑' : '↓'} ${changePercent}%
          </span>
        </div>
        <div class="mt-1 flex items-baseline">
          <span class="text-gray-400 line-through mr-2">${oldPrice}</span>
          <span class="text-lg font-medium">${newPrice}</span>
        </div>
      </div>
    `;
  }
}

// Initialize a global instance
export const priceTracker = new PriceHistory();
