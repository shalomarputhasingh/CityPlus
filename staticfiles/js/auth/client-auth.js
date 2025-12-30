import { supabase } from "../supabase.js";

/* =========================
   OTP LOGIN (FIRST TIME)
========================= */
const phoneInput = document.getElementById("phone");
const otpInput = document.getElementById("otp");
const sendOtpBtn = document.getElementById("sendOtp");
const verifyOtpBtn = document.getElementById("verifyOtp");

sendOtpBtn?.addEventListener("click", async () => {
  const phone = phoneInput.value.trim();
  if (!phone) return alert("Enter phone number");

  const { error } = await supabase.auth.signInWithOtp({ phone });
  if (error) return alert(error.message);

  alert("OTP sent");
  otpInput.style.display = "block";
  verifyOtpBtn.style.display = "block";
});

verifyOtpBtn?.addEventListener("click", async () => {
  const phone = phoneInput.value.trim();
  const token = otpInput.value.trim();

  const { data, error } = await supabase.auth.verifyOtp({
    phone,
    token,
    type: "sms"
  });

  if (error) return alert(error.message);

  const userId = data.user.id;

  const { data: profile } = await supabase
    .from("profiles")
    .select("id")
    .eq("id", userId)
    .single();

  if (!profile) {
    // First time user
    window.location.href = "set-credentials.html";
  } else {
    // Existing user
    window.location.href = "report-issue.html";
  }
});

/* =========================
   USERNAME + PASSWORD LOGIN
========================= */
const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");
const loginBtn = document.getElementById("loginBtn");

loginBtn?.addEventListener("click", async () => {
  const username = usernameInput.value.trim();
  const password = passwordInput.value.trim();

  if (!username || !password) {
    return alert("Enter username and password");
  }

  const email = `${username}@citypulse.local`;

  const { error } = await supabase.auth.signInWithPassword({
    email,
    password
  });

  if (error) return alert("Invalid login");

  window.location.href = "report-issue.html";
});
