// assets/js/cart.js
import { supabase, getCurrentUser } from './supabase.js';

function q(sel){return document.querySelector(sel);} function qs(sel){return document.querySelectorAll(sel);}function fmt(c){return (c/100).toLocaleString(undefined,{style:'currency',currency:'USD'});}

async function ensureData(){
  const user=await getCurrentUser();
  if(!user){ q('#cartContainer').innerHTML='<p class="text-center">Please log in to view your cart.</p>'; return; }
  const { data: cart } = await supabase.from('carts').select('*').eq('user_id',user.id).eq('status','open').single();
  if(!cart){ q('#cartContainer').innerHTML='<p class="text-center">Your cart is empty.</p>'; return; }
  const { data: items } = await supabase.from('cart_items').select('*, products(*)').eq('cart_id',cart.id);
  render(items);
}

function render(items){
  if(!items.length){ q('#cartContainer').innerHTML='<p class="text-center">Your cart is empty.</p>'; return; }
  let total=0;
  const rows=items.map(it=>{
    const p=it.products; const subtotal=it.qty * p.price_cents; total+=subtotal;
    return `<tr><td class="p-2">${p.title}</td><td class="p-2">${fmt(p.price_cents)}</td><td class="p-2">${it.qty}</td><td class="p-2">${fmt(subtotal)}</td></tr>`;
  }).join('');
  q('#cartBody').innerHTML=rows;
  q('#cartTotal').textContent=fmt(total);
}

document.addEventListener('DOMContentLoaded',ensureData);
