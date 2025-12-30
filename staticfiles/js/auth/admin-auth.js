// js/auth/admin-auth.js
import { supabase } from "../supabase.js";

const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const loginBtn = document.getElementById("adminLogin");

loginBtn.addEventListener("click", async () => {
  const email = emailInput.value.trim();
  const password = passwordInput.value.trim();

  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password
  });

  if (error) {
    alert(error.message);
    return;
  }

  // Check admin role
  const userId = data.user.id;

  const { data: admin } = await supabase
    .from("admins")
    .select("*")
    .eq("id", userId)
    .single();

  if (!admin) {
    alert("Not an admin");
    await supabase.auth.signOut();
    return;
  }

  window.location.href = "admin-dashboard.html";
});
