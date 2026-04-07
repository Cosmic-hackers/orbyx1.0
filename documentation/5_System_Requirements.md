# 5. System Requirements

The ORBYX platform utilizes a cloud-native, containerized architecture that separates the heavy Python calculations from the user's local hardware. This ensures maximum compatibility.

## 5.1 Server-Side Requirements
- **OS Platform:** Linux (Debian/Ubuntu-based environments).
- **Environment:** Container Server (e.g., Render Web Services) with Python 3.11.
- **Memory (RAM):** 512MB RAM minimum (to support `uvicorn`, `folium` rendering, and heavy TLE memory caches).
- **Network Interface:** Outbound internet access to continuously poll Space-Track/Celestrak datasets.

## 5.2 Client-Side Requirements
- **Browser:** Any modern Web Browser (Google Chrome >= 90, Safari >= 14, Mozilla Firefox >= 88).
- **Hardware:** Minimal specifications required. Any iOS, Android, macOS, or Windows device manufactured within the past 7 years can smoothly handle the SPA mapping overlays.
- **Network:** Active internet connection to successfully load mapped raster tiles (OpenStreetMap tiles and Plotly visual assets).
