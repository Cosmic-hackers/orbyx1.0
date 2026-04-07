# 3. Project Overview

## 3.1 Description
ORBYX is a fully integrated, full-stack Single Page Application (SPA) designed to solve the UI/UX issues of legacy satellite tracking software. The backend acts as a highly optimized abstraction layer that caches TLE data from global databases and performs intensive SGP4 orbital mechanics calculations using the `skyfield` Python library. It then streams these positions into a visually stunning, responsive cyberpunk dashboard utilizing `Folium` and `Plotly` for plotting capabilities.

## 3.2 Key Functionalities
- **Instant Search:** Allows users to query an active catalog of ~8000+ satellites by string matching names or exact NORAD ID.
- **Multi-Perspective Viewing:**
  - **2D Mercator Tracker:** Shows the orbital track history and future projection over a standard Earth map.
  - **3D Orthographic Globe:** Offers a realistic, rotatable 3-dimensional perspective displaying the satellite constellation webs.
  - **Sky-View Radar:** Features a topocentric polar plot, charting azimuth (angle around the horizon) and elevation (angle above the horizon) based exactly on the user's localized coordinates.
- **Pass Predictions Engine:** Automatically calculates Acquisition of Signal (AOS), Peak Altitude (MAX), and Loss of Signal (LOS) times for the next 24 hours.
- **Persistent Storage:** Maintains user ground station settings and saved "Constellation" tracking lists dynamically via cached JSON without database overhead.
- **Sydh AI Agent:** A conversational cyber-assistant engineered into a stylized command prompt that assists with answering questions regarding features and application statuses.
