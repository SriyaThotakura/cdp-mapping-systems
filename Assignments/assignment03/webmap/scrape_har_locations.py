import json
import requests
import folium
from folium.plugins import MarkerCluster
from pathlib import Path
from typing import List, Tuple
import os
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from functools import lru_cache

# === CONFIGURATION ===
HAR_FILE = "inputs/nationalgeographic.com.har"  # Replace with your HAR filename
OUTPUT_MAP = "outputs/ip_map.html"
MAX_IPS = 50  # Limit to avoid API rate limiting
TIMEOUT = (5, 10)  # (connect, read) seconds
RETRIES = 2
BACKOFF = 0.5
RATE_LIMIT_DELAY = 0.2  # seconds between calls to avoid rate limits
IPINFO_TOKEN = os.getenv("IPINFO_TOKEN", "").strip()
GEOIP2_DB = os.getenv("GEOIP2_DB", "data/GeoLite2-City.mmdb").strip()

# Create a shared HTTP session with retries/backoff
def _make_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=RETRIES,
        connect=RETRIES,
        read=RETRIES,
        backoff_factor=BACKOFF,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.headers.update({"User-Agent": "geolocate-har-file/1.0"})
    return s

SESSION = _make_session()

# Lazily import geoip2 when DB is present
def _get_geoip_reader():
    try:
        if GEOIP2_DB and os.path.isfile(GEOIP2_DB):
            import geoip2.database  # type: ignore

            return geoip2.database.Reader(GEOIP2_DB)
    except Exception as e:
        print(f"Failed to open GeoIP2 DB at '{GEOIP2_DB}': {e}")
    return None

_GEOIP_READER = None

# === FUNCTIONS ===


def load_ips_from_har(path: str) -> List[str]:
    """Extract unique IP addresses from a HAR file."""
    with open(path, "r", encoding="utf-8") as f:
        har = json.load(f)

    entries = har.get("log", {}).get("entries", [])
    ips = set()
    for entry in entries:
        ip = entry.get("serverIPAddress")
        url = entry.get("request", {}).get("url", "")
        print(f"Processing entry: {url} with IP: {ip}")
        if ip:
            # print(f"Found IP: {ip}")
            ip = ip.strip("[]")
            ips.add((ip, url))
    return list(ips)


@lru_cache(maxsize=1024)
def _geolocate_ip_no_url(ip: str) -> Tuple[float, float]:
    """Internal: resolve IP to (lat, lon) using local DB first, then providers."""
    global _GEOIP_READER

    # Local DB first (offline)
    if _GEOIP_READER is None:
        _GEOIP_READER = _get_geoip_reader()
    if _GEOIP_READER is not None:
        try:
            resp = _GEOIP_READER.city(ip)
            loc = resp.location
            if loc and loc.latitude is not None and loc.longitude is not None:
                return float(loc.latitude), float(loc.longitude)
        except Exception as e:
            # Continue to network fallbacks
            print(f"Local GeoIP2 lookup failed for {ip}: {e}")

    # Network providers
    def _ipinfo_lookup(ip: str):
        headers = {}
        if IPINFO_TOKEN:
            headers["Authorization"] = f"Bearer {IPINFO_TOKEN}"
        resp = SESSION.get(f"https://ipinfo.io/{ip}/json", headers=headers, timeout=TIMEOUT)
        data = resp.json()
        loc = data.get("loc")
        if loc:
            lat, lon = map(float, loc.split(","))
            return lat, lon
        return None

    def _ipapi_lookup(ip: str):
        resp = SESSION.get(f"https://ipapi.co/{ip}/json/", timeout=TIMEOUT)
        data = resp.json()
        lat = data.get("latitude") or data.get("lat")
        lon = data.get("longitude") or data.get("lon")
        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
            return float(lat), float(lon)
        return None

    def _ipwhois_lookup(ip: str):
        resp = SESSION.get(f"https://ipwho.is/{ip}", timeout=TIMEOUT)
        data = resp.json()
        if data.get("success"):
            lat = data.get("latitude")
            lon = data.get("longitude")
            if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                return float(lat), float(lon)
        return None

    def _ipapi_com_lookup(ip: str):
        resp = SESSION.get(f"http://ip-api.com/json/{ip}?fields=status,message,lat,lon", timeout=TIMEOUT)
        data = resp.json()
        if data.get("status") == "success":
            lat = data.get("lat")
            lon = data.get("lon")
            if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                return float(lat), float(lon)
        return None

    providers = [
        ("ipinfo", _ipinfo_lookup),
        ("ipapi", _ipapi_lookup),
        ("ipwhois", _ipwhois_lookup),
        ("ip-api", _ipapi_com_lookup),
    ]

    for name, fn in providers:
        try:
            result = fn(ip)
            time.sleep(RATE_LIMIT_DELAY)
            if result:
                return result
        except Exception as e:
            print(f"Error locating {ip} via {name}: {e}")

    return 0.0, 0.0


def geolocate_ip(ip_item: Tuple[str, str]) -> Tuple[str, float, float, str]:
    """Geolocate IP using local DB (if available) then online providers. Returns (ip, lat, lon, url)."""
    ip, url = ip_item
    lat, lon = _geolocate_ip_no_url(ip)
    return ip, lat, lon, url


def build_map(
    ip_locations: List[Tuple[str, float, float, str]], output_path: str
) -> None:
    """Generate Folium map from list of IP + lat/lon tuples."""
    # Ensure outputs directory exists
    Path("outputs").mkdir(parents=True, exist_ok=True)
    m = folium.Map(location=[20, 0], zoom_start=2)
    cluster = MarkerCluster().add_to(m)
    for ip, lat, lon, url in ip_locations:
        if lat and lon:
            folium.Marker(
                location=[lat, lon],
                popup=f"IP: {ip}<br>URL: {url}",
                icon=folium.Icon(color="blue", icon="info-sign"),
            ).add_to(cluster)

    # additionally save data as a GeoJSON file
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"ip": ip, "url": url},
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat],
                },
            }
            for ip, lat, lon, url in ip_locations
            if lat and lon
        ],
    }

    m.save(output_path)
    print(f"Map saved to: {output_path}")

    # additionally save data as a GeoJSON file
    with open("outputs/ip_locations.geojson", "w", encoding="utf-8") as f:
        json.dump(geojson_data, f, ensure_ascii=False, indent=2)
    print("GeoJSON saved to: outputs/ip_locations.geojson")


# === RUN ===

if __name__ == "__main__":
    ip_list = load_ips_from_har(HAR_FILE)
    print(f"Found {len(ip_list)} IPs")

    # ip_list is a list of (ip, url) tuples; deduplicate by IP only
    ips_dict = {}
    for ip, url in ip_list:
        if ip not in ips_dict:
            ips_dict[ip] = url
    ips = list(ips_dict.items())
    print(f"Unique IPs: {len(ips)}")
    ip_locations = [geolocate_ip(ip) for ip in ips[:MAX_IPS]]
    build_map(ip_locations, OUTPUT_MAP)
