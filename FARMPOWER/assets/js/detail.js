// assets/js/detail.js
import { supabase, getCurrentUser } from './supabase.js';

function q(sel){return document.querySelector(sel);} // shortcut

function priceFmt(cents){return (cents/100).toLocaleString(undefined,{style:'currency',currency:'USD'});}

async function loadProduct(id){
  const { data, error } = await supabase.from('products').select('*').eq('id', id).single();
  if(error){ console.error(error); q('#detailContainer').innerHTML='<p class="text-red-500">Product not found.</p>'; return; }
  render(data);
}

function render(p){
  q('#prodImg').src = p.image_url || 'https://source.unsplash.com/800x600?tractor';
  q('#prodTitle').textContent = p.title;
  q('#prodDesc').textContent = p.description || '';
  q('#prodPrice').textContent = priceFmt(p.price_cents);
  document.title = p.title + ' - FarmPower';
  q('#addCartBtn').addEventListener('click', ()=> addToCart(p.id));
}

async function ensureOpenCart(uid){
  const { data } = await supabase.from('carts').select('*').eq('user_id', uid).eq('status','open').single();
  if(data) return data.id;
  const { data: created } = await supabase.from('carts').insert({user_id:uid}).select().single();
  return created.id;
}
async function addToCart(product_id){
  const user = await getCurrentUser();
  if(!user){ alert('Please log in first'); return; }
  const cart_id = await ensureOpenCart(user.id);
  await supabase.from('cart_items').upsert({cart_id,product_id,qty:1});
  alert('Added to cart');
}

// init
const urlParams = new URLSearchParams(window.location.search);
const pid = urlParams.get('id');
if(pid){ loadProduct(pid); }
