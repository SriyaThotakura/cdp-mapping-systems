// Create a map and set its view to a specific location and zoom level
var map = L.map("map").setView([40.70491, -73.97144], 13);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: "© OpenStreetMap contributors",
}).addTo(map);

// Create a layer group for the markers
const markers = L.layerGroup().addTo(map);

// Add a loading indicator
const loading = L.control({ position: 'topright' });
loading.onAdd = function() {
  this._div = L.DomUtil.create('div', 'loading-indicator');
  this._div.innerHTML = 'Loading pizza data...';
  return this._div;
};
loading.addTo(map);

// Fetch pizza restaurant data from the NYC Open Data API
fetch(
  "https://data.cityofnewyork.us/resource/43nn-pn8j.geojson?cuisine_description=Pizza&$limit=10000"
)
  .then((response) => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then((data) => {
    // Remove loading indicator
    map.removeControl(loading);
    
    // Add a count of restaurants to the title
    const count = data.features.length;
    const countElement = document.createElement('p');
    countElement.className = 'restaurant-count';
    countElement.textContent = `Showing ${count} pizza restaurants`;
    document.querySelector('.title-container').appendChild(countElement);
    
    // Process the data to format it for Leaflet
    data.features.forEach((feature) => {
      // Add geometry property to each feature
      if (feature.properties && feature.properties.latitude && feature.properties.longitude) {
        feature.geometry = {
          type: "Point",
          coordinates: [
            Number(feature.properties.longitude),
            Number(feature.properties.latitude)
          ]
        };
      }
    });
    
    // Filter out any features without valid geometry
    const validFeatures = data.features.filter(feature => feature.geometry);
    const geoJsonData = {
      type: "FeatureCollection",
      features: validFeatures
    };
    
    // Create GeoJSON layer with circle markers
    L.geoJSON(geoJsonData, {
      pointToLayer: function (feature, latlng) {
        return L.circleMarker(latlng, {
          radius: 8,
          fillColor: "#e74c3c",
          color: "#fff",
          weight: 1,
          opacity: 1,
          fillOpacity: 0.8
        });
      },
      onEachFeature: function(feature, layer) {
        // Add popup with just the restaurant name
        if (feature.properties && feature.properties.dba) {
          layer.bindPopup(feature.properties.dba);
        }
      }
    }).addTo(markers);
    
    // Fit the map to show all markers
    if (validFeatures.length > 0) {
      const bounds = markers.getBounds();
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [50, 50] });
      }
    }
    
    console.log(`Data loaded successfully: ${validFeatures.length} valid pizza restaurants found`);
  })
  .catch((error) => {
    console.error("Error fetching data:", error);
    // Update loading indicator to show error
    const errorDiv = document.querySelector('.loading-indicator');
    if (errorDiv) {
      errorDiv.textContent = 'Error loading data. Please try again later.';
      errorDiv.style.color = '#e74c3c';
    }
  });

  const { createClient } = supabase;

  const supabaseUrl = 'https://sb_publishable_PPRbeiJQBcj5XS2tUBwnCQ_NaU3DNio.supabase.co'; // ← your actual Supabase URL
  const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNidGdyZHRzYXR5cmN6dnpqbXhwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMzOTQyNjUsImV4cCI6MjA2ODk3MDI2NX0.Iycf9-K3SCuLVJnGLJht68YOOKGsNuD4Z0mQQ0AlhoM-anon-key';                         // ← your anon public key
  
  const supabaseClient = createClient(sb_publishable_PPRbeiJQBcj5XS2tUBwnCQ_NaU3DNio, eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNidGdyZHRzYXR5cmN6dnpqbXhwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMzOTQyNjUsImV4cCI6MjA2ODk3MDI2NX0.Iycf9-K3SCuLVJnGLJht68YOOKGsNuD4Z0mQQ0AlhoM);
  
  async function querySupabase() {
    const { data, error } = await supabaseClient
        .from("open-restaurant-inspections")
        .select("*")
        .limit(100);

    if (error) {
        console.error("Error fetching data:", error);
    } else {
        console.log("Data fetched successfully:", data);
    }
}
window.supabase

document.addEventListener("DOMContentLoaded", () => {
  querySupabase();
});