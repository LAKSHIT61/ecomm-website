document.addEventListener("DOMContentLoaded",()=>{
 const id=Number(new URLSearchParams(location.search).get("id")||1);
 const target=document.getElementById("product-detail");
 (window.productsReady||Promise.resolve()).then(()=>{
   const p=PRODUCTS.find(x=>x.id===id)||PRODUCTS[0];
   target.innerHTML=`<div class="product-visual"><img src="${p.image}" alt="${p.name}"></div><div class="product-info"><span class="product-category">${p.category}</span><h1>${p.name}</h1><div class="rating"><span>★★★★★</span> <small>${p.rating} (${p.reviews})</small></div><p class="large-price">${money(p.price)} ${p.oldPrice?`<del>${money(p.oldPrice)}</del>`:""}</p><p>${p.description}</p><p class="stock-note">${p.stock>0?`${p.stock} available`:`Currently out of stock`}</p><button class="btn btn-primary" ${p.stock===0?"disabled":""} onclick="addToCart(${p.id})">Add to cart</button><a class="text-link" href="shop.html">← Continue shopping</a></div>`;
 });
});
