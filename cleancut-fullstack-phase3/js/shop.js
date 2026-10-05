document.addEventListener("DOMContentLoaded",()=>{
 const target=document.getElementById("shop-products"),search=document.getElementById("search-input"),filter=document.getElementById("category-filter");
 if(!target||!search||!filter)return;
 const params=new URLSearchParams(location.search);filter.value=params.get("category")||"all";
 function render(){const q=search.value.toLowerCase();const cat=filter.value;renderProducts(target,PRODUCTS.filter(p=>(cat==="all"||p.category===cat)&&p.name.toLowerCase().includes(q)));}
 search.addEventListener("input",render);filter.addEventListener("change",render);
 (window.productsReady||Promise.resolve()).then(render);
});
