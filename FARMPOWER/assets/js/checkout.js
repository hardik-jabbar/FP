// assets/js/checkout.js
import { supabase, getCurrentUser } from './supabase.js';

function q(sel){return document.querySelector(sel);}function fmt(c){return (c/100).toLocaleString(undefined,{style:'currency',currency:'USD'});}

async function loadSummary(){
  const user=await getCurrentUser();
  if(!user){q('#checkoutContainer').innerHTML='<p>Please log in.</p>';return;}
  const { data: cart } = await supabase.from('carts').select('*').eq('user_id',user.id).eq('status','open').single();
  if(!cart){q('#checkoutContainer').innerHTML='<p>Your cart is empty.</p>';return;}
  const { data: items } = await supabase.from('cart_items').select('qty, products(id,title,price_cents)').eq('cart_id',cart.id);
  let total=0; items.forEach(i=> total+=i.qty*i.products.price_cents);
  q('#orderTotal').textContent=fmt(total);
  q('#payBtn').addEventListener('click',()=> pay(cart.id));
}
async function pay(cart_id){
  const { data, error } = await supabase.rpc('checkout',{cart_id});
  if(error){ alert('Checkout failed'); console.error(error); return; }
  window.location.href='orders.html';
}

document.addEventListener('DOMContentLoaded',loadSummary);
