// assets/js/marketplace.js
// Generic marketplace front-end helpers powered by Supabase.
import { supabase, getCurrentUser } from './supabase.js';

/** Render a product card element */
function productCard(p) {
  const price = (p.price_cents / 100).toLocaleString(undefined, { style: 'currency', currency: 'USD' });
  return `<div class="card-hover bg-dark-200 rounded-lg overflow-hidden animate-fade-in" data-id="${p.id}">
    <img src="${p.image_url || 'https://source.unsplash.com/600x400?tractor'}" alt="${p.title}" class="w-full h-48 object-cover">
    <div class="p-4 flex flex-col h-full">
      <h3 class="text-lg font-semibold mb-2">${p.title}</h3>
      <p class="text-gray-400 flex-grow">${p.description ?? ''}</p>
      <div class="mt-4 flex items-center justify-between">
        <span class="text-xl font-bold">${price}</span>
        <button class="addCart px-3 py-1 bg-primary text-white rounded-md hover:bg-primary/90">Add to Cart</button>
      </div>
    </div>
  </div>`;
}

async function loadProducts(filter = {}) {
  let query = supabase.from('products').select('*').eq('is_active', true);
  if (filter.category_id) query = query.eq('category_id', filter.category_id);
  const { data, error } = await query.limit(60);
  if (error) {
    console.error(error);
    return [];
  }
  return data;
}

async function ensureOpenCart(user_id) {
  const { data, error } = await supabase.from('carts')
    .select('*')
    .eq('user_id', user_id)
    .eq('status', 'open')
    .single();
  if (data) return data.id;
  // create new
  const { data: created, error: err2 } = await supabase.from('carts').insert({ user_id }).select().single();
  if (err2) throw err2;
  return created.id;
}

async function addToCart(product_id) {
  const user = await getCurrentUser();
  if (!user) return alert('Please log in first');
  const cart_id = await ensureOpenCart(user.id);
  await supabase.from('cart_items').upsert({ cart_id, product_id, qty: 1 });
  alert('Added to cart');
}

function wireEvents(container) {
  container.addEventListener('click', (e) => {
    const btn = e.target.closest('.addCart');
    if (!btn) return;
    const card = btn.closest('[data-id]');
    addToCart(Number(card.dataset.id));
  });
}

// Auto-init on pages containing #tractorGrid or #partsGrid etc.
document.addEventListener('DOMContentLoaded', async () => {
  const grid = document.getElementById('tractorGrid') || document.getElementById('partsGrid') || document.getElementById('featuredGrid');
  if (!grid) return; // not a marketplace page
  const categoryMap = {
    tractors: 1,
    parts: 2,
  };
  const category_id = grid.id.includes('parts') ? categoryMap.parts : undefined;
  const products = await loadProducts({ category_id });
  grid.innerHTML = products.map(productCard).join('');
  wireEvents(grid);
});
