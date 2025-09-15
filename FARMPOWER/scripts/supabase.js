import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://fmqxdoocmapllbuecblc.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZtcXhkb29jbWFwbGxidWVjYmxjIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTQ2NjUyMjYsImV4cCI6MjAxMDI0MTIyNn0.Fk1PiWHtCiCWus6nhgVrF_n7LSt9G5VuhDCCXYFPqE4'

export const supabase = createClient(supabaseUrl, supabaseKey)

// Equipment related functions
export const equipmentApi = {
  async createListing(data) {
    const { data: equipment, error } = await supabase
      .from('equipment')
      .insert([data])
      .select()
      .single();

    if (error) throw error;
    return equipment;
  },

  async getListings({ page = 1, limit = 12, category = null, filters = {} }) {
    let query = supabase
      .from('equipment')
      .select('*, profiles!equipment_owner_id_fkey(full_name)', { count: 'exact' })
      .eq('is_active', true)
      .eq('is_approved', true);

    if (category) {
      query = query.eq('category', category);
    }

    // Apply filters
    if (filters.brand) query = query.eq('brand', filters.brand);
    if (filters.minPrice) query = query.gte('price', filters.minPrice);
    if (filters.maxPrice) query = query.lte('price', filters.maxPrice);
    if (filters.condition) query = query.eq('condition', filters.condition);
    if (filters.minYear) query = query.gte('year', filters.minYear);
    if (filters.maxYear) query = query.lte('year', filters.maxYear);

    // Pagination
    const from = (page - 1) * limit;
    query = query.range(from, from + limit - 1);

    const { data, error, count } = await query;
    if (error) throw error;

    return { data, count };
  },

  async getListing(id) {
    const { data, error } = await supabase
      .from('equipment')
      .select(`
        *,
        profiles!equipment_owner_id_fkey(
          full_name,
          email,
          is_seller,
          seller_rating
        ),
        reviews(*)
      `)
      .eq('id', id)
      .single();

    if (error) throw error;
    return data;
  },

  async updateListing(id, data) {
    const { data: equipment, error } = await supabase
      .from('equipment')
      .update(data)
      .eq('id', id)
      .select()
      .single();

    if (error) throw error;
    return equipment;
  },

  async deleteListing(id) {
    const { error } = await supabase
      .from('equipment')
      .delete()
      .eq('id', id);

    if (error) throw error;
  }
};

// Order related functions
export const orderApi = {
  async createOrder(data) {
    const { data: order, error } = await supabase
      .from('orders')
      .insert([data])
      .select()
      .single();

    if (error) throw error;
    return order;
  },

  async getUserOrders() {
    const { data, error } = await supabase
      .from('orders')
      .select(`
        *,
        equipment(*),
        profiles!buyer_id_fkey(full_name),
        profiles!seller_id_fkey(full_name)
      `)
      .order('created_at', { ascending: false });

    if (error) throw error;
    return data;
  },

  async updateOrderStatus(id, status) {
    const { data: order, error } = await supabase
      .from('orders')
      .update({ status })
      .eq('id', id)
      .select()
      .single();

    if (error) throw error;
    return order;
  }
};

// Review related functions
export const reviewApi = {
  async createReview(data) {
    const { data: review, error } = await supabase
      .from('reviews')
      .insert([data])
      .select()
      .single();

    if (error) throw error;
    return review;
  },

  async getEquipmentReviews(equipmentId) {
    const { data, error } = await supabase
      .from('reviews')
      .select(`
        *,
        profiles!reviewer_id_fkey(full_name)
      `)
      .eq('equipment_id', equipmentId)
      .order('created_at', { ascending: false });

    if (error) throw error;
    return data;
  }
};

// Wishlist related functions
export const wishlistApi = {
  async addToWishlist(equipmentId) {
    const { data, error } = await supabase
      .from('wishlists')
      .insert([{ equipment_id: equipmentId }])
      .select()
      .single();

    if (error) throw error;
    return data;
  },

  async removeFromWishlist(equipmentId) {
    const { error } = await supabase
      .from('wishlists')
      .delete()
      .eq('equipment_id', equipmentId);

    if (error) throw error;
  },

  async getUserWishlist() {
    const { data, error } = await supabase
      .from('wishlists')
      .select('*, equipment(*)')
      .order('created_at', { ascending: false });

    if (error) throw error;
    return data;
  }
};

// Message related functions
export const messageApi = {
  async sendMessage(data) {
    const { data: message, error } = await supabase
      .from('messages')
      .insert([data])
      .select()
      .single();

    if (error) throw error;
    return message;
  },

  async getConversations() {
    const { data, error } = await supabase
      .from('messages')
      .select(`
        *,
        sender:profiles!sender_id_fkey(full_name),
        receiver:profiles!receiver_id_fkey(full_name)
      `)
      .order('created_at', { ascending: false });

    if (error) throw error;
    return data;
  },

  async markAsRead(messageId) {
    const { error } = await supabase
      .from('messages')
      .update({ is_read: true })
      .eq('id', messageId);

    if (error) throw error;
  }
};