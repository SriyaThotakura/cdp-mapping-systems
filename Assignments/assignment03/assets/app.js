/* IP Requests Web Map - client script */
(function(){
  const state = {
    raw: null,
    features: [],
    map: null,
    layer: null,
    query: '',
    baseLayers: null
  };

  const qs = (s, r=document) => r.querySelector(s);
  const qsa = (s, r=document) => Array.from(r.querySelectorAll(s));

  function createMap() {
    const map = L.map('map', { center: [20, 0], zoom: 2 });

    // Base maps
    const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    });
    const positron = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
      subdomains: 'abcd',
      maxZoom: 20
    });
    const darkMatter = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
      subdomains: 'abcd',
      maxZoom: 20
    });

    // Default basemap
    darkMatter.addTo(map);

    const baseLayers = {
      'Dark': darkMatter,
      'Light': positron,
      'OSM': osm
    };
    state.baseLayers = baseLayers;
    L.control.layers(baseLayers, {}, { position: 'topleft' }).addTo(map);

    state.map = map;
  }

  function markerStyle(feature) {
    return {
      radius: 6,
      color: '#60a5fa',
      weight: 2,
      fillColor: '#93c5fd',
      fillOpacity: 0.8
    };
  }

  function bindPopup(feature, layer) {
    const p = feature.properties || {};
    const ip = p.ip || 'Unknown IP';
    const url = p.url || '';
    const isImg = /\.(png|jpg|jpeg|gif|webp|avif)(\?.*)?$/i.test(url);
    const imgHtml = isImg ? `<div class="thumb"><img src="${url}" alt="image" loading="lazy"/></div>` : '';
    const linkHtml = url ? `<a href="${url}" target="_blank" rel="noopener">Open URL</a>` : '';
    const html = `${imgHtml}<div><b>IP:</b> ${ip}<br/><b>URL:</b> ${url || 'N/A'}<br/>${linkHtml}</div>`;
    layer.bindPopup(html);
  }

  function renderLayer() {
    if (state.layer) {
      state.map.removeLayer(state.layer);
      state.layer = null;
    }
    const q = state.query.trim().toLowerCase();
    const filtered = !q ? state.features : state.features.filter(f => {
      const p = f.properties || {};
      return String(p.ip||'').toLowerCase().includes(q) || String(p.url||'').toLowerCase().includes(q);
    });

    const layer = L.geoJSON({ type: 'FeatureCollection', features: filtered }, {
      pointToLayer: (feature, latlng) => L.circleMarker(latlng, markerStyle(feature)),
      onEachFeature: bindPopup
    }).addTo(state.map);
    state.layer = layer;

    // Update list
    const list = qs('#list');
    list.innerHTML = '';
    filtered.forEach((f, idx) => {
      const p = f.properties || {};
      const ip = p.ip || 'Unknown IP';
      const url = p.url || '';
      const el = document.createElement('div');
      el.className = 'item';
      el.innerHTML = `<div><b>${ip}</b></div><small>${url}</small>`;
      el.addEventListener('click', () => {
        const l = state.layer.getLayers()[idx];
        if (l) {
          state.map.setView(l.getLatLng(), 6, { animate: true });
          l.openPopup();
        }
      });
      list.appendChild(el);
    });

    // Update counters
    qs('#count-total').textContent = state.features.length;
    qs('#count-shown').textContent = filtered.length;

    // Fit bounds if there are points
    try {
      const b = layer.getBounds();
      if (b.isValid()) state.map.fitBounds(b.pad(0.2));
    } catch(e) {}
  }

  function wireUI() {
    qs('#search').addEventListener('input', (e) => {
      state.query = e.target.value;
      renderLayer();
    });
    qs('#btn-fit').addEventListener('click', () => renderLayer());
    qs('#btn-clear').addEventListener('click', () => {
      qs('#search').value = '';
      state.query = '';
      renderLayer();
    });
  }

  async function init() {
    createMap();
    wireUI();
    try {
      const resp = await fetch('outputs/ip_locations.geojson');
      if (!resp.ok) throw new Error('Failed to load GeoJSON: ' + resp.status);
      const data = await resp.json();
      state.raw = data;
      state.features = Array.isArray(data.features) ? data.features : [];
      renderLayer();
    } catch (err) {
      console.error(err);
      alert('Could not load outputs/ip_locations.geojson. Make sure you are serving this folder via a local HTTP server.');
    }
  }

  window.addEventListener('DOMContentLoaded', init);
})();
