// js/supabase.js
import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm";

// Prefer values from `window` (set by js/config.js). If missing, fall back to the
// hardcoded demo project so the app still runs as a demo.
const SUPABASE_URL = window.SUPABASE_URL || "https://emyjskqartiteqysgedk.supabase.co";
const SUPABASE_ANON_KEY = window.SUPABASE_ANON_KEY || "sb_publishable_rvuzVAcNQF8OwAb08NyLNQ_WgveQ2JX";

export const supabase = createClient(
  SUPABASE_URL,
  SUPABASE_ANON_KEY,
  {
    auth: {
      persistSession: true,
      autoRefreshToken: true
    }
  }
);

// Also expose as a global for non-module pages if needed
try {
  window.supabase = window.supabase || {};
  window.supabaseClient = window.supabaseClient || supabase;
} catch (e) {
  // noop in some sandboxed environments
}
