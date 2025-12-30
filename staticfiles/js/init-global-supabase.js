// Loads the UMD Supabase client and creates a global `supabaseClient`.
(function () {
  if (!window.SUPABASE_URL || !window.SUPABASE_ANON_KEY) {
    console.warn("Supabase config missing. Copy js/config.example.js to js/config.js and fill values.");
    // Do not attempt to initialize a real client when config is missing.
    // Provide a helpful stub that fails loudly and clearly when used.
    window.supabaseClient = {
      _notConfigured: true,
      from() { throw new Error("Supabase not configured. Create `js/config.js` from `js/config.example.js` and set `SUPABASE_URL` and `SUPABASE_ANON_KEY`."); }
    };
    return;
  }

  // Load UMD script if `supabase` global is not present
  if (typeof supabase === "undefined") {
    const s = document.createElement("script");
    s.src = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js";
    s.onload = () => {
      try {
        window.supabaseClient = window.supabase.createClient(window.SUPABASE_URL, window.SUPABASE_ANON_KEY);
      } catch (e) {
        console.error("Failed to initialize supabaseClient:", e);
      }
    };
    s.onerror = () => console.error("Failed to load Supabase SDK");
    document.head.appendChild(s);
  } else {
    try {
      window.supabaseClient = window.supabase.createClient(window.SUPABASE_URL, window.SUPABASE_ANON_KEY);
    } catch (e) {
      console.error("Failed to initialize supabaseClient:", e);
    }
  }
})();
