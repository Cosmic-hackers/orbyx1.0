#!/usr/bin/env python3
"""Satellite Orbit Tools — Command-line interface.

Usage:
    python cli.py init          Initialize database and seed ground stations
    python cli.py sync          Fetch TLEs from CelesTrak and populate database
    python cli.py sync --group stations    Sync specific group (default: stations+visual)
    python cli.py sync --all    Sync all major groups (takes a few minutes)
    python cli.py status        Show database status
    python cli.py api           Start FastAPI backend
    python cli.py dashboard     Start Streamlit frontend
"""

import argparse
import sys
import time

from src.config import get_settings
from src.database.models import initialize_database
from src.database.manager import SatelliteDB
from src.logging_config import setup_logging, get_logger
from src.utils.celestrak_client import fetch_tle_group, get_demo_satellites, GROUPS

logger = get_logger("cli")


def _sync_from_spacetrack(object_type: str | None = None, limit: int = 1000) -> list[dict]:
    """Fetch TLE data from Space-Track.org (requires credentials)."""
    import asyncio
    from src.utils.space_track_client import SpaceTrackClient

    async def _fetch():
        async with SpaceTrackClient() as client:
            return await client.fetch_tle_latest(object_type=object_type, limit=limit)

    return asyncio.run(_fetch())


def cmd_init(args):
    """Initialize database and show status."""
    print("Initializing database...")
    initialize_database()
    settings = get_settings()
    print(f"  Database: {settings.db_path}")

    with SatelliteDB() as db:
        count = db.get_satellite_count()
        stations = db.get_ground_stations()
    print(f"  Satellites: {count:,}")
    print(f"  Ground stations: {len(stations)}")
    for s in stations:
        print(f"    - {s['name']} ({s['latitude']:.2f}, {s['longitude']:.2f})")
    print("\nDone! Run 'python cli.py sync' to fetch satellite data.")


def cmd_sync(args):
    """Fetch TLE data and populate database.

    Priority: Space-Track (if credentials set) > CelesTrak > Demo data.
    """
    initialize_database()

    if args.list_groups:
        print("Available CelesTrak groups:")
        for key, desc in GROUPS.items():
            print(f"  {key:20s} {desc}")
        return

    # Demo mode — bundled offline data
    if args.demo:
        print("Loading bundled demo data...")
        satellites = get_demo_satellites()
        with SatelliteDB() as db:
            added, updated = db.upsert_satellites_batch(satellites)
            total_count = db.get_satellite_count()
            db.log_sync(added, updated, total_count, source="demo")
        print(f"Loaded {added} satellites ({updated} updated). Total: {total_count}")
        return

    # Try Space-Track first if credentials are configured
    settings = get_settings()
    if settings.spacetrack_username and settings.spacetrack_password:
        print("Space-Track credentials found. Using Space-Track.org API...")
        _sync_spacetrack(args)
        return

    # Fallback to CelesTrak
    print("No Space-Track credentials. Using CelesTrak (free, no auth)...")
    _sync_celestrak(args)


def _sync_spacetrack(args):
    """Sync from Space-Track.org (primary source)."""
    total_added = 0
    total_updated = 0

    # Space-Track object types
    if args.all:
        categories = [
            ("PAYLOAD", 2000),
            ("ROCKET BODY", 1000),
            ("DEBRIS", 1000),
        ]
    elif args.group:
        categories = [(g.strip().upper(), 1000) for g in args.group.split(",")]
    else:
        categories = [("PAYLOAD", 1000)]

    for obj_type, limit in categories:
        print(f"\nFetching '{obj_type}' (limit={limit})...", end=" ", flush=True)
        start = time.time()
        try:
            satellites = _sync_from_spacetrack(object_type=obj_type, limit=limit)
        except Exception as e:
            print(f"error: {e}")
            continue
        elapsed = time.time() - start

        if not satellites:
            print(f"no data ({elapsed:.1f}s)")
            continue

        print(f"{len(satellites)} satellites ({elapsed:.1f}s)")
        print("  Saving to database...", end=" ", flush=True)

        with SatelliteDB() as db:
            added, updated = db.upsert_satellites_batch(satellites)
            total_count = db.get_satellite_count()
            db.log_sync(added, updated, total_count, source=f"space-track:{obj_type}")

        total_added += added
        total_updated += updated
        print(f"added={added}, updated={updated}")

    print(f"\n{'='*50}")
    print(f"Sync complete: {total_added} added, {total_updated} updated")
    with SatelliteDB() as db:
        print(f"Total satellites in catalog: {db.get_satellite_count():,}")


def _sync_celestrak(args):
    """Sync from CelesTrak (fallback source)."""
    total_added = 0
    total_updated = 0

    if args.all:
        groups = ["stations", "visual", "weather", "science", "geo",
                  "gps-ops", "galileo", "amateur", "resource", "last-30-days"]
    elif args.group:
        groups = [g.strip() for g in args.group.split(",")]
    else:
        groups = ["stations", "visual"]

    for group in groups:
        print(f"\nFetching '{group}'...", end=" ", flush=True)
        start = time.time()
        satellites = fetch_tle_group(group)
        elapsed = time.time() - start

        if not satellites:
            print(f"no data ({elapsed:.1f}s)")
            continue

        print(f"{len(satellites)} satellites ({elapsed:.1f}s)")
        print("  Saving to database...", end=" ", flush=True)

        with SatelliteDB() as db:
            added, updated = db.upsert_satellites_batch(satellites)
            total_count = db.get_satellite_count()
            db.log_sync(added, updated, total_count, source=f"celestrak:{group}")

        total_added += added
        total_updated += updated
        print(f"added={added}, updated={updated}")

    print(f"\n{'='*50}")
    print(f"Sync complete: {total_added} added, {total_updated} updated")
    with SatelliteDB() as db:
        print(f"Total satellites in catalog: {db.get_satellite_count():,}")


def cmd_status(args):
    """Show database and system status."""
    initialize_database()
    settings = get_settings()

    print("Satellite Orbit Tools — Status")
    print(f"{'='*50}")
    print(f"Database: {settings.db_path}")
    print(f"  Exists: {settings.db_path.exists()}")

    with SatelliteDB() as db:
        total = db.get_satellite_count()
        print(f"  Satellites: {total:,}")

        type_stats = db.get_object_type_stats()
        if type_stats:
            print(f"  Types:")
            for t in type_stats:
                print(f"    {t['object_type']:20s} {t['count']:,}")

        stations = db.get_ground_stations()
        print(f"  Ground stations: {len(stations)}")

        history = db.get_sync_history(5)
        if history:
            print(f"\nRecent syncs:")
            for h in history:
                print(f"  {h['sync_time']}  {h['source']:25s}  "
                      f"+{h['satellites_added']}/-{h['satellites_updated']}  "
                      f"total={h['total_in_catalog']:,}  [{h['status']}]")

    print(f"\nAPI: http://{settings.api_host}:{settings.api_port}")
    print(f"Dashboard: http://localhost:{settings.streamlit_port}")


def cmd_api(args):
    """Start FastAPI backend server."""
    import uvicorn
    settings = get_settings()
    initialize_database()
    print(f"Starting API at http://{settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
    )


def cmd_dashboard(args):
    """Start Streamlit frontend."""
    import subprocess
    settings = get_settings()
    initialize_database()
    print(f"Starting dashboard at http://localhost:{settings.streamlit_port}")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "frontend/app.py",
        "--server.port", str(settings.streamlit_port),
        "--server.headless", "true",
    ])


def main():
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Satellite Orbit Tools CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # init
    sub.add_parser("init", help="Initialize database and seed ground stations")

    # sync
    p_sync = sub.add_parser("sync", help="Fetch TLEs from CelesTrak")
    p_sync.add_argument("--group", "-g", help="CelesTrak group(s), comma-separated (default: stations,visual)")
    p_sync.add_argument("--all", "-a", action="store_true", help="Sync all major groups")
    p_sync.add_argument("--list-groups", "-l", action="store_true", help="List available groups")
    p_sync.add_argument("--demo", "-d", action="store_true", help="Load bundled demo data (offline)")

    # status
    sub.add_parser("status", help="Show database and system status")

    # api
    sub.add_parser("api", help="Start FastAPI backend")

    # dashboard
    sub.add_parser("dashboard", help="Start Streamlit frontend")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    commands = {
        "init": cmd_init,
        "sync": cmd_sync,
        "status": cmd_status,
        "api": cmd_api,
        "dashboard": cmd_dashboard,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
