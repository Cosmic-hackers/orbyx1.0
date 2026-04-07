# 12. Limitations

## 12.1 Defined Limitations
- **Cold-Start Delays:** Due to aggressive free-tier platform restrictions (Render Cloud), extreme delays reaching upwards of 50 seconds can occur impacting critical UI interactions if the external API endpoints sleep after 15 minutes of inactivity.
- **Data Extrapolation Inaccuracies:** TLE catalogs age rapidly. SGP4 models degrade concerning long-term estimations; therefore tracking arrays rely strictly upon daily TLE updating procedures otherwise pass events drop substantially below baseline margins of errors.
- **Hardware Acceleration Ceilings:** Folium outputs complex 2-dimensional poly-lines and Geo-Vectors pushing heavy SVG dom structures scaling exponentially over 50+ tracked targets reducing lower-end local CPU client experiences rapidly.
- **Database Scalability:** Relying fundamentally upon a stateless local file `config.json` restricts the app to a single-tenant environment inherently limiting multi-user or authenticated cross-account state tracking architectures.
