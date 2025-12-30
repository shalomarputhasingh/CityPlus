// js/client/otp.js
import { supabase } from "../supabase.js";

const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");
const saveBtn = document.getElementById("saveCredentials");

saveBtn.addEventListener("click", async () => {
  const user_id = usernameInput.value.trim();
  const password = passwordInput.value.trim();

  if (!user_id || !password) {
    alert("All fields required");
    return;
  }

  const { data: userData } = await supabase.auth.getUser();
  const userId = userData.user.id;
  const phone = userData.user.phone;

  // 1️⃣ Update password securely
  const { error: passwordError } = await supabase.auth.updateUser({ password });
  if (passwordError) {
    alert(passwordError.message);
    return;
  }

  // 2️⃣ Save profile data
  const { error } = await supabase.from("profiles").insert({
    id: userId,
    phone,
    user_id,
    first_login_completed: true
  });

  if (error) {
    alert(error.message);
    return;
  }

  alert("Account created successfully");
  window.location.href = "report-issue.html";
});
