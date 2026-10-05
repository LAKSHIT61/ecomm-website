const AUTH_TOKEN_KEY = "cleancut_access_token";
const AUTH_USER_KEY = "cleancut_user";

function getAuthToken(){ return localStorage.getItem(AUTH_TOKEN_KEY); }
function getCurrentUser(){
  try { return JSON.parse(localStorage.getItem(AUTH_USER_KEY) || "null"); }
  catch { return null; }
}
function setAuthSession(data){
  localStorage.setItem(AUTH_TOKEN_KEY, data.access_token);
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify(data.user));
}
function clearAuthSession(){
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(AUTH_USER_KEY);
}

async function syncLocalCart(){
  const cart = JSON.parse(localStorage.getItem("cleancut_cart") || "[]");
  if(!cart.length || !getAuthToken()) return;
  for(const item of cart){
    try{
      const r = await authFetch("/api/cart/items", {method:"POST", body:JSON.stringify({product_id:item.id, quantity:item.qty})});
      if(!r.ok) console.warn("Could not sync cart item", item.id);
    }catch(e){ console.warn("Cart sync failed", e); }
  }
  localStorage.removeItem("cleancut_cart");
}

async function authFetch(path, options={}){
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");
  const token = getAuthToken();
  if(token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(path, {...options, headers});
  if(response.status === 401){
    clearAuthSession();
    if(!location.pathname.endsWith("login.html")) location.href = "login.html";
  }
  return response;
}

function showAuthMessage(message, type="error"){
  const el = document.getElementById("auth-message");
  if(!el) return;
  el.textContent = message;
  el.className = `auth-message ${type}`;
}

function requireAuth(){
  if(!getAuthToken()){
    location.href = `login.html?next=${encodeURIComponent(location.pathname.split("/").pop() || "profile.html")}`;
    return false;
  }
  return true;
}

async function loadProfile(){
  if(!requireAuth()) return;
  try{
    const response = await authFetch("/api/auth/me");
    if(!response.ok) throw new Error((await response.json()).detail || "Could not load profile");
    const user = await response.json();
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
    const name = document.getElementById("profile-name");
    const email = document.getElementById("profile-email");
    const phone = document.getElementById("profile-phone");
    const address = document.getElementById("profile-address");
    if(name) name.value = user.name || "";
    if(email) email.value = user.email || "";
    if(phone) phone.value = user.phone || "";
    if(address) address.value = user.address || "";
    const greeting = document.getElementById("profile-greeting");
    if(greeting) greeting.textContent = `Welcome back, ${user.name.split(" ")[0]}.`;
  }catch(error){ showAuthMessage(error.message, "error"); }
}

document.addEventListener("DOMContentLoaded", async ()=>{
  const signup = document.getElementById("signup-form");
  const login = document.getElementById("login-form");
  const profile = document.getElementById("profile-form");
  const logout = document.getElementById("logout-button");

  if(signup) signup.addEventListener("submit", async (e)=>{
    e.preventDefault();
    const button = signup.querySelector("button[type=submit]");
    button.disabled = true; button.textContent = "Creating account…";
    try{
      const response = await fetch("/api/auth/signup", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({
        name: signup.elements[0].value.trim(), email: signup.elements[1].value.trim(), password: signup.elements[2].value
      })});
      const data = await response.json();
      if(!response.ok) throw new Error(data.detail || "Could not create your account");
      setAuthSession(data);
      await syncLocalCart();
      const next = new URLSearchParams(location.search).get("next") || "profile.html";
      location.href = next;
    }catch(error){ showAuthMessage(error.message, "error"); }
    finally{ button.disabled = false; button.textContent = "Create account"; }
  });

  if(login) login.addEventListener("submit", async (e)=>{
    e.preventDefault();
    const button = login.querySelector("button[type=submit]");
    button.disabled = true; button.textContent = "Signing in…";
    try{
      const response = await fetch("/api/auth/login", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({
        email: login.elements[0].value.trim(), password: login.elements[1].value
      })});
      const data = await response.json();
      if(!response.ok) throw new Error(data.detail || "Could not sign you in");
      setAuthSession(data);
      await syncLocalCart();
      const next = new URLSearchParams(location.search).get("next") || "profile.html";
      location.href = next;
    }catch(error){ showAuthMessage(error.message, "error"); }
    finally{ button.disabled = false; button.textContent = "Login"; }
  });

  if(profile){
    loadProfile();
    profile.addEventListener("submit", async (e)=>{
      e.preventDefault();
      const button = profile.querySelector("button[type=submit]");
      button.disabled = true; button.textContent = "Saving…";
      try{
        const response = await authFetch("/api/auth/me", {method:"PATCH", body:JSON.stringify({
          name: document.getElementById("profile-name").value.trim(),
          email: document.getElementById("profile-email").value.trim(),
          phone: document.getElementById("profile-phone").value.trim() || null,
          address: document.getElementById("profile-address").value.trim() || null
        })});
        const data = await response.json();
        if(!response.ok) throw new Error(data.detail || "Could not save changes");
        localStorage.setItem(AUTH_USER_KEY, JSON.stringify(data));
        showAuthMessage("Profile updated successfully ✓", "success");
      }catch(error){ showAuthMessage(error.message, "error"); }
      finally{ button.disabled = false; button.textContent = "Save changes"; }
    });
  }

  if(logout) logout.addEventListener("click", ()=>{ clearAuthSession(); location.href="index.html"; });
});
