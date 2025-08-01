var map = new maplibregl.Map({
    container: 'map', // container id
    style: 'style.json', // style URL for basemap
    center: [-73.97144, 40.70491], // starting position [lng, lat]
    zoom: 6 // starting zoom
});
map.addControl(new maplibregl.NavigationControl());
