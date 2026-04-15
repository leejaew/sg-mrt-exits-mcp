# sg-mrt-exits Connector Test

I tested the **sg-mrt-exits** connector and confirmed that it is available with **15 tools** focused on Singapore MRT/LRT exit discovery, proximity lookups, tourist guidance, planning, and station-level exit analysis.

## Brief Capability Overview

| Capability area | What it does | Example tool |
|---|---|---|
| Station exit lookup | Lists exits for a station, including wildcard station searches | `search_exits_by_station` |
| Exit detail lookup | Returns a specific exit's coordinates and metadata | `get_exit_detail` |
| Map and directions | Provides Google Maps and directions links for an exit | `get_exit_map_view` |
| Nearest-exit search | Finds the closest exits to coordinates or a landmark | `find_nearest_exit_by_coordinates`, `find_nearest_exit_by_landmark` |
| Radius analysis | Returns all exits within a given distance | `find_exits_within_radius` |
| Line-wide listing | Lists exits across an MRT/LRT line | `list_exits_by_line` |
| Station footprint | Shows the geographic spread of all exits for a station | `get_station_footprint` |
| Retail and urban analysis | Supports site-selection, density, and accessibility-oriented queries | `retail_proximity_analysis`, `urban_planning_exit_density`, `accessibility_check` |
| Logistics and emergency use | Helps with delivery planning and nearest exits for incidents | `logistics_delivery_planning`, `emergency_response_exits` |
| Tourist and commuter guidance | Recommends best exits for attractions or compares exits for a destination | `tourist_guide_exits`, `commuter_exit_comparison` |

## What I Tested

| Test | Result | Notes |
|---|---|---|
| Connector tool discovery | Success | Server exposed 15 tools |
| Live landmark lookup | Success | Returned nearest exits for Marina Bay Sands |
| Exit detail lookup | Success after format correction | The exit code needed the exact format `Exit B`, not `B` |
| Tourist guidance lookup | Success | Returned recommended exit and map links for Gardens by the Bay |
| First live call attempt | Temporary failure | One call hit a degraded MCP connection error before succeeding on retry |

## Example Data Fetched

### 1) Nearest exits to Marina Bay Sands

> Landmark resolved: 'Marina Bay Sands' → 1.2837° N, 103.8607° E
>
> Nearest 3 MRT exit(s):
> 1. Bayfront — Exit B (154 metres)
> 2. Bayfront — Exit C (158 metres)
> 3. Bayfront — Exit D (167 metres)

### 2) Detailed data for Bayfront Exit B

| Field | Value |
|---|---|
| Station | Bayfront |
| Exit code | Exit B |
| Location | 1.2827° N, 103.8598° E |
| Object ID | 17775 |
| Last updated | 2025-12 |

### 3) Tourist guide output for Gardens by the Bay

> Tourist guide — MRT exits near 'Gardens by the Bay':
> 1. Gardens By The Bay — Exit 3 (approximately 399 metres)
> 2. Gardens By The Bay — Exit 1 (approximately 412 metres)
> 3. Gardens By The Bay — Exit 2 (approximately 423 metres)
> 4. Bayfront — Exit B (approximately 604 metres)
> 5. Bayfront — Exit C (approximately 625 metres)
>
> Recommendation: Take **Gardens By The Bay** station and use **Exit 3**.

## How to Use It

You can think of the connector in three practical ways.

First, use it for **simple station lookups** when you already know the station name and want all available exits. Second, use it for **landmark-based guidance** when you know a destination, such as Marina Bay Sands or Gardens by the Bay, and want the closest MRT exit. Third, use it for **planning and analysis** when you need all exits within a radius, density around an area, retail-footfall context, or emergency/logistics support.

## Practical Example Prompts

| Need | Example request |
|---|---|
| Find exits for a station | "Show me all exits at Orchard MRT." |
| Find nearest exit to a place | "Which MRT exit is closest to Marina Bay Sands?" |
| Tourist guidance | "Which MRT exit should I use for Gardens by the Bay?" |
| Compare exits | "Which exit at Dhoby Ghaut is best for Plaza Singapura?" |
| Radius scan | "What MRT exits are within 500m of Suntec City?" |
| Retail analysis | "How many MRT exits are within 300m of this address?" |
| Accessibility-oriented lookup | "Which nearby MRT exits should I check for accessible access near this location?" |

## Bottom Line

The connector is **working**, and I successfully fetched live MRT exit data from it. The main limitation observed during testing was a **temporary degraded connection error** on one attempt, but subsequent calls succeeded and returned usable data.

If you want, I can next run a few more sample queries for a place you care about in Singapore and show you the exact outputs.
