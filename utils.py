import json
import os
import requests
from skyfield.api import load, EarthSatellite, wgs84
from datetime import datetime, timezone, timedelta

CONFIG_FILE = "config.json"
TLE_DATA_DIR = "tle_cache"

if not os.path.exists(TLE_DATA_DIR):
    os.makedirs(TLE_DATA_DIR)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"satellites": [], "ground_station": {"name": "Default", "latitude": 0, "longitude": 0, "elevation_m": 0}}
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def fetch_active_catalog():
    """Celestrak'tan tüm aktif uyduların listesini indirir ve cache'ler."""
    cache_path = os.path.join(TLE_DATA_DIR, "active_catalog.txt")
    
    # Günde sadece 1 kez indir
    if os.path.exists(cache_path):
        file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_path))
        if file_age < timedelta(hours=24):
            with open(cache_path, 'r') as f:
                return f.read().splitlines()

    print("📡 Aktif uydu kataloğu indiriliyor (Celestrak)...")
    # Güncel Celestrak GP API URL'si
    url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        with open(cache_path, 'wb') as f:
            f.write(response.content)
        return response.text.splitlines()
    except Exception as e:
        print(f"❌ Katalog indirilemedi: {e}")
        return []

def get_satellite_from_catalog(name_or_id):
    """Katalog içinde isim veya NORAD ID ile arama yapar, TLE döner."""
    catalog = fetch_active_catalog()
    # Yalnızca geçerli TLE satırlarını arayalım
    for i in range(len(catalog) - 2):
        if catalog[i+1].startswith("1 ") and catalog[i+2].startswith("2 "):
            name = catalog[i].strip()
            line1 = catalog[i+1]
            line2 = catalog[i+2]
            parts = line2.split()
            if len(parts) > 1:
                norad_id = parts[1]
                if str(name_or_id).upper() in name.upper() or str(name_or_id) == norad_id:
                    return name, line1, line2
    return None

def get_active_satellites():
    """Config'deki uyduları ve seçili analiz uydusunu döner."""
    config = load_config()
    ts = load.timescale()
    sat_objects = []
    
    for sat_info in config.get('satellites', []):
        data = get_satellite_from_catalog(sat_info['norad_id'])
        if data:
            sat_objects.append(EarthSatellite(data[1], data[2], data[0], ts))
    
    return sat_objects, config

def get_ground_station():
    config = load_config()
    gs = config['ground_station']
    return wgs84.latlon(gs['latitude'], gs['longitude'], gs.get('elevation_m', 0)), gs

def get_upcoming_passes(satellite, ground_station, hours=24):
    """Belirli bir uydu için yer istasyonundan görünecek geçişleri hesaplar."""
    ts = load.timescale()
    now = datetime.now(timezone.utc)
    t0 = ts.from_datetime(now)
    t1 = ts.from_datetime(now + timedelta(hours=hours))
    
    # 10 derece üzerindeki geçişleri bul (altitude > 10)
    t, events = satellite.find_events(ground_station, t0, t1, altitude_degrees=10.0)
    
    passes = []
    current_pass = {}
    
    for ti, event in zip(t, events):
        name = ('Rise', 'Culminate', 'Set')[event]
        diff = (satellite - ground_station).at(ti)
        alt, az, dist = diff.altaz()
        
        event_data = {
            "time": ti.utc_strftime('%H:%M:%S'),
            "datetime": ti.utc_datetime(),
            "azimuth": round(az.degrees, 1),
            "elevation": round(alt.degrees, 1),
            "type": name
        }
        
        if event == 0: # AOS (Rise)
            current_pass = {"aos": event_data}
        elif event == 1: # MAX (Peak)
            current_pass["max"] = event_data
        elif event == 2: # LOS (Set)
            if "aos" in current_pass:
                current_pass["los"] = event_data
                current_pass["satellite"] = satellite.name
                # Süre hesapla
                duration = (current_pass['los']['datetime'] - current_pass['aos']['datetime']).total_seconds() / 60
                current_pass["duration_min"] = round(duration, 1)
                passes.append(current_pass)
                current_pass = {}
                
    return passes



if __name__ == "__main__":
    # Test
    ts = load.timescale()
    sats, cfg = get_active_satellites()
    gs, _ = get_ground_station()
    if sats:
        print(f"📡 {sats[0].name} için geçişler hesaplanıyor...")
        p = get_upcoming_passes(sats[0], gs)
        print(f"✅ {len(p)} geçiş bulundu.")
    


if __name__ == "__main__":
    # Test etmek için basit bir kontrol
    try:
        sats, cfg = get_active_satellites()
        print(f"\n🚀 Test: {len(sats)} uydu başarıyla çekildi.")
    except Exception as e:
        print(f"🔴 Test hatası: {e}")
