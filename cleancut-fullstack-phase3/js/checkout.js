document.addEventListener("DOMContentLoaded",()=>{
 const summary=document.getElementById("checkout-summary"),form=document.getElementById("checkout-form");if(!summary||!form)return;
 if(!requireAuth())return;
 let cart=null;
 const load=async()=>{try{
   const cartResponse=await authFetch("/api/cart");cart=await cartResponse.json();if(!cartResponse.ok)throw new Error(cart.detail||"Could not load your bag");
   if(!cart.items.length){summary.innerHTML='<p>Your bag is empty.</p><a class="text-link" href="shop.html">Continue shopping →</a>';form.querySelector("button[type=submit]").disabled=true;return;}
   summary.innerHTML=cart.items.map(i=>`<p>${i.product.name} × ${i.quantity}<strong>${money(i.line_total)}</strong></p>`).join("")+`<hr><h3>Total ${money(cart.total)}</h3>`;
   try{const pr=await authFetch("/api/auth/me");if(pr.ok){const u=await pr.json();form.elements.full_name.value=u.name||"";form.elements.phone.value=u.phone||"";form.elements.address.value=u.address||"";}}catch(e){}
 }catch(err){summary.innerHTML=`<p>${err.message}</p>`;}};
 load();
 form.addEventListener("submit",async e=>{e.preventDefault();
   const button=form.querySelector("button[type=submit]"), method=form.elements.payment.value;
   button.disabled=true;button.textContent=method==="online"?"Opening payment…":"Placing order…";
   const payload={full_name:form.elements.full_name.value.trim(),phone:form.elements.phone.value.trim(),address:form.elements.address.value.trim(),city:form.elements.city.value.trim(),pincode:form.elements.pincode.value.trim()};
   try{
     if(method==="cod"){
       const r=await authFetch("/api/orders",{method:"POST",body:JSON.stringify({...payload,payment_method:"cod"})});
       const data=await r.json();if(!r.ok)throw new Error(data.detail||"Could not place order");
       localStorage.removeItem("cleancut_cart");updateCartCount();alert(`Order ${data.order_number} placed successfully ✓`);location.href="orders.html";return;
     }
     const r=await authFetch("/api/payments/razorpay/order",{method:"POST",body:JSON.stringify(payload)});const data=await r.json();if(!r.ok)throw new Error(data.detail||"Could not start payment");
     if(!window.Razorpay)throw new Error("Payment checkout could not load. Please refresh and try again.");
     const options={key:data.key_id,amount:data.amount,currency:data.currency,name:"CleanCut",description:`Order ${data.order_number}`,order_id:data.razorpay_order_id,prefill:{name:payload.full_name,contact:payload.phone},notes:{order_number:data.order_number},theme:{color:"#111111"},handler:async response=>{
       try{
         const verify=await authFetch("/api/payments/razorpay/verify",{method:"POST",body:JSON.stringify({internal_order_number:data.order_number,razorpay_order_id:response.razorpay_order_id,razorpay_payment_id:response.razorpay_payment_id,razorpay_signature:response.razorpay_signature})});
         const result=await verify.json();if(!verify.ok)throw new Error(result.detail||"Payment verification failed");
         localStorage.removeItem("cleancut_cart");updateCartCount();alert(`Payment successful. Order ${result.order_number} confirmed ✓`);location.href="orders.html";
       }catch(err){alert(err.message);button.disabled=false;button.textContent="Pay securely";}
     },modal:{ondismiss:()=>{button.disabled=false;button.textContent="Pay securely";}}};
     const rzp=new Razorpay(options);rzp.on("payment.failed",resp=>{alert(resp.error?.description||"Payment failed. Please try again.");button.disabled=false;button.textContent="Pay securely";});rzp.open();
   }catch(err){alert(err.message);button.disabled=false;button.textContent=method==="online"?"Pay securely":"Place order";}
 });
});
