document.addEventListener("DOMContentLoaded", () => {

  const map = L.map("map", {
    center: [10.0104, 77.4768],
    zoom: 11,
    dragging: false,
    scrollWheelZoom: false,
    doubleClickZoom: false,
    zoomControl: false
  });

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);

  L.marker([10.0104, 77.4768])
    .addTo(map)
    .bindPopup("Theni District")
    .openPopup();
});
