// Small utility helpers used across the client
export function showAlert(msg) {
  alert(msg);
}

export function formatDate(iso) {
  try { return new Date(iso).toLocaleString(); } catch (e) { return iso; }
}
