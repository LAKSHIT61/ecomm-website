function getCart(){return JSON.parse(localStorage.getItem("cleancut_cart")||"[]");}
function saveCart(cart){localStorage.setItem("cleancut_cart",JSON.stringify(cart));updateCartCount();}
function updateCartCount(){const count=getCart().reduce((s,i)=>s+i.qty,0);document.querySelectorAll(".cart-count").forEach(e=>e.textContent=count);}
function addToCart(id){const cart=getCart();const item=cart.find(i=>i.id===id);if(item)item.qty++;else cart.push({id,qty:1});saveCart(cart);alert("Added to cart ✓");}
function money(n){return "₹"+Number(n).toLocaleString("en-IN");}
function productCard(p){
 const discount=p.oldPrice?Math.round((1-p.price/p.oldPrice)*100):0;
 return `<article class="product-card">
   <a href="product.html?id=${p.id}">
    <div class="product-image">
      ${p.tag?`<span class="product-badge">${p.tag}</span>`:""}
      <button class="wishlist" onclick="event.preventDefault();toggleWish(this)" aria-label="Wishlist">♡</button>
      <img src="${p.image}" alt="${p.name}" loading="lazy">
    </div>
   </a>
   <span class="product-category">${p.category}</span>
   <h3 class="product-name">${p.name}</h3>
   <div class="rating"><span>★★★★★</span> <small>${p.rating} (${p.reviews})</small></div>
   <div class="price-row"><strong>${money(p.price)}</strong>${p.oldPrice?`<del>${money(p.oldPrice)}</del><em>${discount}% OFF</em>`:""}</div>
   <button class="add-cart" onclick="addToCart(${p.id})">🛒 &nbsp; Add to Cart</button>
 </article>`;
}
function renderProducts(target,items){target.innerHTML=items.map(productCard).join("");}
document.addEventListener("DOMContentLoaded",()=>{updateCartCount();const featured=document.getElementById("featured-products");if(featured)renderProducts(featured,PRODUCTS.slice(0,4));const ai=document.getElementById("ai-button");if(ai)ai.addEventListener("click",()=>{const input=document.getElementById("ai-input");const out=document.getElementById("ai-response");out.textContent=input.value?`Demo AI: I'd recommend starting with products related to "${input.value}". Full AI integration comes next.`:"Tell me what you're looking for.";});});

function toggleWish(btn){btn.textContent=btn.textContent==="♡"?"♥":"♡";}
