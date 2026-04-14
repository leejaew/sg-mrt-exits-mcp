"""
Live benchmark for all 15 sg-mrt-exits-mcp tools.

Measures:
  - Cold-cache latency (first call, forces API fetch)
  - Warm-cache latency (subsequent calls, served from memory)
  - Concurrent load (8 simultaneous tool calls)

Run with: python benchmark.py
"""
import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))

# ── Realistic Singapore test coordinates ────────────────────────────────────
MARINA_BAY_SANDS   = (1.2838, 103.8607)
ORCHARD_ROAD       = (1.3048, 103.8318)
RAFFLES_PLACE      = (1.2840, 103.8513)
BISHAN             = (1.3510, 103.8480)

# Known stations from the API (TEL partial rollout)
STATION_BRIGHT_HILL    = "BRIGHT HILL MRT STATION"
STATION_CALDECOTT      = "CALDECOTT MRT STATION"
STATION_UPPER_THOMSON  = "UPPER THOMSON MRT STATION"

PASS = "PASS"
FAIL = "FAIL"
results: list[dict] = []


def _colour(status: str) -> str:
    return f"\033[92m{status}\033[0m" if status == PASS else f"\033[91m{status}\033[0m"


async def _run(label: str, coro) -> tuple[float, str]:
    """Run a coroutine, time it, record pass/fail, and print immediately."""
    t0 = time.perf_counter()
    try:
        out = await coro
        elapsed = time.perf_counter() - t0
        ok = not (isinstance(out, str) and out.startswith("API ") or
                  out.startswith("Unable") or out.startswith("Unexpected"))
        status = PASS if ok else FAIL
        preview = out.split("\n")[0][:80] if isinstance(out, str) else repr(out)[:80]
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        status = FAIL
        preview = f"{type(exc).__name__}: {exc}"

    results.append({"label": label, "status": status, "ms": elapsed * 1000})
    colour = _colour(status)
    print(f"  {colour}  {elapsed * 1000:7.1f} ms  {label}")
    print(f"             ↳ {preview}")
    return elapsed, out


async def main() -> None:
    print("\nsg-mrt-exits-mcp — Live Benchmark")
    print("=" * 60)

    # ── Import all tools ───────────────────────────────────────────────────
    from tools.search_tools   import search_exits_by_station, get_exit_detail
    from tools.map_tools      import get_exit_map_view
    from tools.spatial_tools  import (
        find_nearest_exit_by_coordinates,
        find_nearest_exit_by_landmark,
        find_exits_within_radius,
        urban_planning_exit_density,
    )
    from tools.line_tools     import list_exits_by_line, get_station_footprint
    from tools.location_tools import (
        retail_proximity_analysis,
        accessibility_check,
        logistics_delivery_planning,
    )
    from tools.navigation_tools import (
        emergency_response_exits,
        tourist_guide_exits,
        commuter_exit_comparison,
    )
    from api_client import _cache

    # ══════════════════════════════════════════════════════════════════════
    # PHASE 1 — Cold cache (cache empty, first call must hit the API)
    # ══════════════════════════════════════════════════════════════════════
    print("\n── Phase 1: Cold cache (API fetch required) ──────────────────")
    _cache["data"] = None
    _cache["ts"] = 0.0

    await _run("search_exits_by_station('Bright Hill')",
        search_exits_by_station("Bright Hill"))

    _cache["data"] = None; _cache["ts"] = 0.0
    await _run("get_exit_detail('Bright Hill', 'A')",
        get_exit_detail("Bright Hill", "A"))

    _cache["data"] = None; _cache["ts"] = 0.0
    await _run("get_exit_map_view('Caldecott', 'A')",
        get_exit_map_view("Caldecott", "A"))

    _cache["data"] = None; _cache["ts"] = 0.0
    lat, lng = MARINA_BAY_SANDS
    await _run("find_nearest_exit_by_coordinates(Marina Bay Sands, top_n=5)",
        find_nearest_exit_by_coordinates(lat, lng, top_n=5))

    _cache["data"] = None; _cache["ts"] = 0.0
    await _run("find_exits_within_radius(500m, Raffles Place coords)",
        find_exits_within_radius(500, latitude=RAFFLES_PLACE[0], longitude=RAFFLES_PLACE[1]))

    _cache["data"] = None; _cache["ts"] = 0.0
    await _run("urban_planning_exit_density(1000m, Orchard Road coords)",
        urban_planning_exit_density(1000, latitude=ORCHARD_ROAD[0], longitude=ORCHARD_ROAD[1]))

    _cache["data"] = None; _cache["ts"] = 0.0
    await _run("list_exits_by_line('TEL')",
        list_exits_by_line("TEL"))

    _cache["data"] = None; _cache["ts"] = 0.0
    await _run("get_station_footprint('Bright Hill')",
        get_station_footprint("Bright Hill"))

    _cache["data"] = None; _cache["ts"] = 0.0
    await _run("retail_proximity_analysis(500m, Bishan coords)",
        retail_proximity_analysis(500, latitude=BISHAN[0], longitude=BISHAN[1]))

    _cache["data"] = None; _cache["ts"] = 0.0
    await _run("accessibility_check(500m, Marina Bay Sands coords)",
        accessibility_check(500, latitude=MARINA_BAY_SANDS[0], longitude=MARINA_BAY_SANDS[1]))

    _cache["data"] = None; _cache["ts"] = 0.0
    await _run("emergency_response_exits(top_n=3, Raffles Place coords)",
        emergency_response_exits(3, latitude=RAFFLES_PLACE[0], longitude=RAFFLES_PLACE[1]))

    _cache["data"] = None; _cache["ts"] = 0.0
    await _run("logistics_delivery_planning(400m, Orchard Road coords)",
        logistics_delivery_planning(400, latitude=ORCHARD_ROAD[0], longitude=ORCHARD_ROAD[1]))

    _cache["data"] = None; _cache["ts"] = 0.0
    await _run("commuter_exit_comparison('Upper Thomson')",
        commuter_exit_comparison("Upper Thomson"))

    # ══════════════════════════════════════════════════════════════════════
    # PHASE 2 — Warm cache (cache populated, no API calls expected)
    # ══════════════════════════════════════════════════════════════════════
    print("\n── Phase 2: Warm cache (served from memory) ──────────────────")

    await _run("search_exits_by_station('Caldecott')",
        search_exits_by_station("Caldecott"))

    await _run("get_exit_detail('Upper Thomson', 'A')",
        get_exit_detail("Upper Thomson", "A"))

    lat, lng = ORCHARD_ROAD
    await _run("find_nearest_exit_by_coordinates(Orchard Road, top_n=3)",
        find_nearest_exit_by_coordinates(lat, lng, top_n=3))

    await _run("find_exits_within_radius(1000m, Bishan coords)",
        find_exits_within_radius(1000, latitude=BISHAN[0], longitude=BISHAN[1]))

    await _run("urban_planning_exit_density(2000m, Raffles Place coords)",
        urban_planning_exit_density(2000, latitude=RAFFLES_PLACE[0], longitude=RAFFLES_PLACE[1]))

    await _run("list_exits_by_line('CCL')",
        list_exits_by_line("CCL"))

    await _run("get_station_footprint('Caldecott')",
        get_station_footprint("Caldecott"))

    await _run("retail_proximity_analysis(300m, Raffles Place coords)",
        retail_proximity_analysis(300, latitude=RAFFLES_PLACE[0], longitude=RAFFLES_PLACE[1]))

    await _run("accessibility_check(1000m, Bishan coords)",
        accessibility_check(1000, latitude=BISHAN[0], longitude=BISHAN[1]))

    await _run("emergency_response_exits(top_n=5, Orchard Road coords)",
        emergency_response_exits(5, latitude=ORCHARD_ROAD[0], longitude=ORCHARD_ROAD[1]))

    await _run("logistics_delivery_planning(500m, Marina Bay Sands coords)",
        logistics_delivery_planning(500, latitude=MARINA_BAY_SANDS[0], longitude=MARINA_BAY_SANDS[1]))

    await _run("commuter_exit_comparison('Bright Hill')",
        commuter_exit_comparison("Bright Hill"))

    # ══════════════════════════════════════════════════════════════════════
    # PHASE 3 — Geocoding tools (hit Nominatim live, rate-limited 1 req/s)
    # ══════════════════════════════════════════════════════════════════════
    print("\n── Phase 3: Geocoding tools (Nominatim, live, 1 req/sec) ─────")

    await _run("find_nearest_exit_by_landmark('Marina Bay Sands', top_n=3)",
        find_nearest_exit_by_landmark("Marina Bay Sands", top_n=3))

    await _run("tourist_guide_exits('Gardens by the Bay')",
        tourist_guide_exits("Gardens by the Bay"))

    await _run("commuter_exit_comparison('Bright Hill', destination_landmark='Lentor Modern')",
        commuter_exit_comparison("Bright Hill", destination_landmark="Lentor Modern"))

    await _run("retail_proximity_analysis(500m, 'Bishan Junction 8')",
        retail_proximity_analysis(500, landmark_name="Bishan Junction 8"))

    await _run("emergency_response_exits(top_n=3, 'Raffles Hotel')",
        emergency_response_exits(3, landmark_name="Raffles Hotel"))

    # ══════════════════════════════════════════════════════════════════════
    # PHASE 4 — Concurrent load (8 simultaneous warm-cache calls)
    # ══════════════════════════════════════════════════════════════════════
    print("\n── Phase 4: Concurrent load (8 simultaneous calls, warm cache) ")
    t_conc_start = time.perf_counter()
    await asyncio.gather(
        search_exits_by_station("Bright Hill"),
        find_nearest_exit_by_coordinates(*MARINA_BAY_SANDS, top_n=3),
        find_exits_within_radius(500, latitude=RAFFLES_PLACE[0], longitude=RAFFLES_PLACE[1]),
        list_exits_by_line("TEL"),
        retail_proximity_analysis(500, latitude=BISHAN[0], longitude=BISHAN[1]),
        accessibility_check(500, latitude=ORCHARD_ROAD[0], longitude=ORCHARD_ROAD[1]),
        emergency_response_exits(3, latitude=MARINA_BAY_SANDS[0], longitude=MARINA_BAY_SANDS[1]),
        commuter_exit_comparison("Caldecott"),
    )
    t_conc_total = (time.perf_counter() - t_conc_start) * 1000
    print(f"  Total wall time for 8 concurrent calls: {t_conc_total:.1f} ms")

    # ══════════════════════════════════════════════════════════════════════
    # PHASE 5 — Validation guardrails (bad inputs rejected without API hit)
    # ══════════════════════════════════════════════════════════════════════
    print("\n── Phase 5: Input validation guardrails ──────────────────────")

    await _run("find_nearest_exit_by_coordinates(invalid lat=99.0)",
        find_nearest_exit_by_coordinates(99.0, 103.8, top_n=3))

    await _run("find_exits_within_radius(radius=0)",
        find_exits_within_radius(0, latitude=1.3, longitude=103.8))

    await _run("find_exits_within_radius(radius=999999)",
        find_exits_within_radius(999_999, latitude=1.3, longitude=103.8))

    await _run("find_nearest_exit_by_coordinates(lat outside SG)",
        find_nearest_exit_by_coordinates(35.6, 139.7, top_n=3))

    await _run("search_exits_by_station(empty string)",
        search_exits_by_station(""))

    await _run("emergency_response_exits(top_n=0)",
        emergency_response_exits(0, latitude=1.3, longitude=103.8))

    await _run("emergency_response_exits(top_n=999)",
        emergency_response_exits(999, latitude=1.3, longitude=103.8))

    # ══════════════════════════════════════════════════════════════════════
    # SUMMARY
    # ══════════════════════════════════════════════════════════════════════
    phase1 = [r for r in results if "Phase" not in r["label"]]
    cold = [r for r in results[:13]]
    warm = [r for r in results[13:25]]

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results if r["status"] == PASS)
    failed = sum(1 for r in results if r["status"] == FAIL)
    print(f"\nTotal calls:  {len(results)}")
    print(f"  {_colour(PASS)}: {passed}")
    print(f"  {_colour(FAIL)}: {failed}")

    if cold:
        cold_ms = [r["ms"] for r in cold]
        print(f"\nCold cache latency:")
        print(f"  min {min(cold_ms):.1f} ms  |  max {max(cold_ms):.1f} ms  |  avg {sum(cold_ms)/len(cold_ms):.1f} ms")

    if warm:
        warm_ms = [r["ms"] for r in warm]
        print(f"\nWarm cache latency:")
        print(f"  min {min(warm_ms):.1f} ms  |  max {max(warm_ms):.1f} ms  |  avg {sum(warm_ms)/len(warm_ms):.1f} ms")

    if failed:
        print(f"\nFailed calls:")
        for r in results:
            if r["status"] == FAIL:
                print(f"  • {r['label']}")

    print()


if __name__ == "__main__":
    asyncio.run(main())
