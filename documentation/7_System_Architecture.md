# 7. System Architecture

The overarching system architecture implements a modular Full-Stack Model-View-Controller (MVC) paradigm geared specifically toward cloud optimization on platforms like Render.

1. **The Data Layer:** 
   - A localized file-driven JSON storage (`config.json`) maintains stateful data elements like tracked user constellations and manual ground station coordinate configurations. 
   - Telemetry data is handled by fetching raw text logs from Celestrak, managed by the backend, which caches the entire global catalog into an ephemeral active cache (`active_catalog.txt` limit: 24hrs) to strictly avoid API rate limiting constraints.
2. **The Logic/Controller Layer (FastAPI):**
   - The primary application logic resides concurrently in `app.py` and `utils.py`. The controller listens to incoming HTTP traffic (e.g. users sending coordinates, adding satellites). 
   - Before forwarding responses, it invokes mapping engine protocols (`generate_2d_map`, `generate_3d_map`) ensuring dynamically produced interactive artifacts sync with the user's saved list before returning output responses back to the UI.
3. **The Presentation Layer:**
   - The user interface is driven primarily via `index.html` processed by the powerful `Jinja2` templating engine. The rendering context mixes in live server states inside the Single Page Application, continuously looping asynchronous updates visually to strictly separate execution constraints from the UI thread.
