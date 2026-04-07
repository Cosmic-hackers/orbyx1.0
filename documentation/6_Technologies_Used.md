# 6. Technologies Used

## 6.1 Frontend Technology
- **HTML5:** Structures the semantic layout and provides the iframe elements utilized to house dynamic map containers rendering isolated DOM content.
- **Vanilla CSS:** Powers the custom cyberpunk "Glassmorphism" UI, neon-cyan terminal borders, the stylized loader overlay, and media-query responsiveness for mobile and desktop devices.
- **JavaScript (Vanilla):** Orchestrates the Single Page Application mechanics. It communicates with backend REST APIs via `fetch()`, manually parses the returned DOM to refresh sidebars seamlessly without breaking immersion, models the continuous live clock telemetry, and runs the embedded "Sydh AI" interactive console.

## 6.2 Backend Technology
- **Python (>=3.9):** The core algorithmic framework powering computations.
- **FastAPI:** A high-performance Python web framework responsible for routing the API endpoints and handling localized form data securely via `python-multipart`.
- **Skyfield:** A high-precision astronomy library handling SGP4 physical models. Converting deep-space Two-Line Element sets into strictly geocentric coordinate data structures utilized for mapping computations.
- **Folium & Plotly:** Map engines responsible for translating calculated coordinate data series into visually interactive 2D graphs and orthographic projections.
- **Uvicorn:** A lightning-fast ASGI server implementation responsible for serving the application.
