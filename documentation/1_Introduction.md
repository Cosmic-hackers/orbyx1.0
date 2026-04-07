# 1. Introduction

With the accelerating privatization of the space sector, thousands of new artificial satellites are launched annually. Keeping track of specific satellites, whether for radio communication, astrophotography, or orbital safety, demands tools capable of processing complex physical parameters into human-readable data instantly. The ORBYX Tracking System serves as a modernized mission control dashboard to fulfill these observation tracking needs.

## 1.1 Objectives
The primary objectives of the ORBYX project are as follows:
- **Data Democratization:** Abstract away the intimidating mathematics of SGP4 orbital propagation, allowing everyday users to track any active satellite.
- **Visual Clarity:** Provide multiple high-fidelity perspectives (2D, 3D, and Sky-Radar) within a single Web Application to fully contextualize a satellite's spatial location.
- **Predictive Intelligence:** Compute upcoming overhead passes accurately based on standard Two-Line Element (TLE) datasets and custom ground station telemetry.
- **Immersion:** Implement a unique, cohesive cyberpunk UI/UX design (raw terminal elements, fluid animations) that mimics a professional space command station.

## 1.2 Problem Statements
Despite open access to orbital data, several challenges persist for casual observers:
- **Fragmentation of Tools:** Existing tracking tools usually specialize in one view (e.g., only a 2D map or only a text-based pass-time table) forcing users to switch platforms.
- **Poor Aesthetic & UI Design:** Legacy tracking portals often rely on dated, cluttered web 1.0 interfaces that are difficult to navigate on mobile devices.
- **Data Latency:** Many tracking applications require heavy manual refreshes, lacking Single Page Application (SPA) functionality or silent background API caching.
- **Complex Onboarding:** Finding specific satellites requires users to memorize complex NORAD Catalog IDs rather than searching by plain text names.
