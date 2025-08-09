// Minimal Leaflet map init and basic UI hooks

// Initialize map
const mapEl = document.getElementById('map');
const map = L.map(mapEl, {
  center: [20, 0],
  zoom: 2,
  worldCopyJump: true,
});

// Basemap
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; OpenStreetMap contributors',
}).addTo(map);

// Track all markers added (placeholder for future data)
const markers = [];

// Fit button
const btnFit = document.getElementById('btn-fit');
btnFit?.addEventListener('click', () => {
  if (markers.length) {
    const group = L.featureGroup(markers);
    map.fitBounds(group.getBounds().pad(0.2));
  } else {
    map.setView([20, 0], 2);
  }
});

// Clear button (resets search input and any list content)
const btnClear = document.getElementById('btn-clear');
const searchInput = document.getElementById('search');
const list = document.getElementById('list');
btnClear?.addEventListener('click', () => {
  if (searchInput) searchInput.value = '';
  if (list) list.innerHTML = '';
});

// Search input (no dataset yet; set up event for future filtering)
if (searchInput) {
  searchInput.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase();
    // Placeholder: when you have data, filter your items here and update `#list`
    // For now, just show the query text
    list.innerHTML = q ? `<div>Searching for: <strong>${q}</strong></div>` : '';
  });
}

// Counts (placeholders)
const countShown = document.getElementById('count-shown');
const countTotal = document.getElementById('count-total');
if (countShown) countShown.textContent = '0';
if (countTotal) countTotal.textContent = '0';
