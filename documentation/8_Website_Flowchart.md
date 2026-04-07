# 8. Website Flowchart

The ORBYX Tracking System follows a cyclic, event-driven user flow characteristic of dynamic dashboards.

1. **Initialization:** User boots the URL.
2. **Boot Sequence:** 
   - Backend spins up, parses TLE catalogs, calculates 2D/3D map tiles.
   - Frontend overlays a purely aesthetic "Hacking Terminal" loading effect hiding initial load stutter.
3. **Main Dashboard:** 
   - Left Sidebar: User configures target ground station coordinates. User adds custom satellites or browses current tracked constellations. 
   - Center Display: Interactive tracking toggles seamlessly shift viewing focus between the global Earth map and localized 3-dimensional globes dynamically populated via backend routing arrays.
4. **Pass Prediction (Asynchronous):** System routinely checks for "Next Pass" event triggers based on the local time against parsed UTC time codes. It displays visually striking on-screen alerts ~15 minutes before Acquisitions of Signal (AOS).
5. **AI Consultation:** At any time, the user interacts with the "Sydh AI" terminal prompt located in the footer logic loop to troubleshoot platform details or retrieve situational context regarding specific functions.
