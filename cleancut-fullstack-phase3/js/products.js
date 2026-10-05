const LOCAL_PRODUCTS = [
 {id:1,name:"Gentle Face Cleanser",category:"skincare",price:499,oldPrice:699,tag:"Bestseller",rating:4.8,reviews:"1.2K",image:"assets/images/cleanser.jpg",description:"A gentle everyday cleanser designed to leave skin feeling fresh, clean and comfortable.",stock:120},
 {id:2,name:"Glow Serum",category:"skincare",price:899,oldPrice:1299,tag:"Bestseller",rating:4.9,reviews:"2.1K",image:"assets/images/serum.jpg",description:"A lightweight glow serum designed for a hydrated, luminous-looking complexion.",stock:85},
 {id:3,name:"Daily Moisturizer",category:"beauty",price:699,oldPrice:999,tag:"New",rating:4.7,reviews:"980",image:"assets/images/moisturizer.jpg",description:"An everyday moisturizer designed to keep skin feeling soft and hydrated.",stock:95},
 {id:4,name:"Facial Roller Set",category:"tools",price:599,oldPrice:899,tag:"Trending",rating:4.6,reviews:"843",image:"assets/images/roller.jpg",description:"A simple facial massage set for an elevated self-care routine.",stock:60},
 {id:5,name:"Sun Defense SPF 50",category:"skincare",price:699,oldPrice:999,tag:"Popular",rating:4.8,reviews:"1.4K",image:"assets/images/sunscreen.jpg",description:"Daily sun protection for a comfortable, easy-to-layer routine.",stock:140},
 {id:6,name:"Hydrating Lip Mask",category:"beauty",price:399,oldPrice:599,tag:"Bestseller",rating:4.7,reviews:"920",image:"assets/images/lip-mask.jpg",description:"A nourishing lip mask designed for soft, hydrated-looking lips.",stock:110}
];

let PRODUCTS = [...LOCAL_PRODUCTS];
async function loadProducts(){try{const r=await fetch("/api/products");if(!r.ok)throw 0;const p=await r.json();if(Array.isArray(p)&&p.length)PRODUCTS=p;}catch(e){console.info("CleanCut API unavailable; using local demo catalogue.");}document.dispatchEvent(new CustomEvent("products:ready"));return PRODUCTS;}
window.productsReady=loadProducts();

function getCart(){return JSON.parse(localStorage.getItem("cleancut_cart")||"[]");}
function saveCart(cart){localStorage.setItem("cleancut_cart",JSON.stringify(cart));updateCartCount();}
function updateCartCount(){const count=getCart().reduce((s,i)=>s+i.qty,0);document.querySelectorAll(".cart-count").forEach(e=>e.textContent=count);}
async function addToCart(id){
 const product=PRODUCTS.find(p=>p.id===id);
 if(product&&product.stock===0){alert("This product is currently out of stock.");return;}
 if(typeof getAuthToken === "function" && getAuthToken()){
   try{
     const r=await authFetch("/api/cart/items",{method:"POST",body:JSON.stringify({product_id:id,quantity:1})});
     const data=await r.json(); if(!r.ok) throw new Error(data.detail||"Could not add to cart");
     window.serverCart=data; updateServerCartCount(data); alert("Added to your bag ✓"); return;
   }catch(e){if(e.message) alert(e.message); return;}
 }
 const cart=getCart(),item=cart.find(i=>i.id===id);if(item)item.qty++;else cart.push({id,qty:1});saveCart(cart);alert("Added to bag ✓");
}
function updateServerCartCount(cart){const count=cart?.item_count||0;document.querySelectorAll(".cart-count").forEach(e=>e.textContent=count);}
function money(n){return "₹"+Number(n).toLocaleString("en-IN");}
function productCard(p){const discount=p.oldPrice?Math.round((1-p.price/p.oldPrice)*100):0;return `<article class="product-card"><a href="product.html?id=${p.id}"><div class="product-image">${p.tag?`<span class="product-badge">${p.tag}</span>`:""}<button class="wishlist" onclick="event.preventDefault();toggleWish(this)" aria-label="Wishlist">♡</button><img src="${p.image}" alt="${p.name}" loading="lazy"></div></a><span class="product-category">${p.category}</span><h3 class="product-name">${p.name}</h3><div class="rating"><span>★★★★★</span> <small>${p.rating} (${p.reviews})</small></div><div class="price-row"><strong>${money(p.price)}</strong>${p.oldPrice?`<del>${money(p.oldPrice)}</del><em>${discount}% OFF</em>`:""}</div><button class="add-cart" onclick="addToCart(${p.id})">🛒 &nbsp; Add to Cart</button></article>`;}
function renderProducts(target,items){if(target)target.innerHTML=items.map(productCard).join("");}
function renderFeatured(){const featured=document.getElementById("featured-products");if(featured)renderProducts(featured,PRODUCTS.slice(0,4));const ai=document.getElementById("ai-button");if(ai&&!ai.dataset.bound){ai.dataset.bound="true";ai.addEventListener("click",()=>{const input=document.getElementById("ai-input"),out=document.getElementById("ai-response");out.textContent=input.value?`Demo AI: I'd recommend starting with products related to "${input.value}". Full AI integration comes next.`:"Tell me what you're looking for.";});}}
document.addEventListener("DOMContentLoaded",()=>{updateCartCount();if(window.productsReady)window.productsReady.then(renderFeatured);});
document.addEventListener("products:ready",renderFeatured);
function toggleWish(btn){btn.textContent=btn.textContent==="♡"?"♥":"♡";}
