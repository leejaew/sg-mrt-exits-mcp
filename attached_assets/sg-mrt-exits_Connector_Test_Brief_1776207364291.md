# sg-mrt-exits Connector Test Brief

I tested the **sg-mrt-exits** connector and also verified the underlying Singapore MRT exit dataset that the service advertises. The result is mixed: the connector endpoint page is reachable and clearly documents its toolset, but the configured connector call did **not** complete successfully from this environment during the test run.

| Item | Result |
| --- | --- |
| MCP server listed in environment | Yes |
| Landing page reachable | Yes |
| Advertised tool count | 15 |
| Direct connector call via CLI | Failed during connection setup |
| Underlying MRT exit dataset fetch | Succeeded |
| Total exits confirmed from fetched dataset | 597 |

## What happened in the test

The connector landing page at [sg-mrt-exits-mcp.replit.app](https://sg-mrt-exits-mcp.replit.app/) loaded successfully and described the available features. However, direct connector testing failed when attempting to list tools or check server connectivity. The observed errors included an OAuth-related initialization failure and an `EOF` error when posting to the `/mcp` endpoint. That suggests the connector configuration or transport layer likely needs attention before it can be used reliably through the current MCP client setup.

| Diagnostic step | Observation |
| --- | --- |
| List tools | Failed with OAuth-related connection initialization error |
| Auth status | Reported HTTP server, OAuth not supported |
| Server check | Failed with `Post ... /mcp: EOF` |

## Capabilities brief

Based on the connector's own landing page, **sg-mrt-exits** is designed to answer Singapore MRT/LRT exit questions with structured tools. It covers station lookup, single-exit details, nearest-exit search, radius search, accessibility checks, tourist guidance, logistics support, emergency routing, retail proximity analysis, and urban-planning density analysis.

| Capability area | Example tool |
| --- | --- |
| Station lookup | `search_exits_by_station` |
| Exact exit details | `get_exit_detail` |
| Map and directions | `get_exit_map_view` |
| Nearest exit to coordinates | `find_nearest_exit_by_coordinates` |
| Nearest exit to a place name | `find_nearest_exit_by_landmark` |
| Exits within a radius | `find_exits_within_radius` |
| Station spatial spread | `get_station_footprint` |
| All exits on a line | `list_exits_by_line` |
| Accessibility guidance | `accessibility_check` |
| Tourist routing | `tourist_guide_exits` |
| Retail and footfall context | `retail_proximity_analysis` |
| Delivery planning | `logistics_delivery_planning` |
| Emergency response | `emergency_response_exits` |
| Area density analysis | `urban_planning_exit_density` |

## Sample data successfully fetched

Although the connector itself did not execute successfully, I fetched the official MRT exit GeoJSON dataset that the service wraps and confirmed live records are available.

| Station name | Exit code | Longitude | Latitude | Updated |
| --- | --- | ---: | ---: | --- |
| BRIGHT HILL MRT STATION | Exit 1 | 103.833635 | 1.364037 | 20251202172807 |
| BRIGHT HILL MRT STATION | Exit 2 | 103.833511 | 1.363283 | 20251202172807 |
| BRIGHT HILL MRT STATION | Exit 4 | 103.831954 | 1.363164 | 20251202172807 |
| BRIGHT HILL MRT STATION | Exit 3 | 103.832376 | 1.362184 | 20251202172807 |
| UPPER THOMSON MRT STATION | Exit 2 | 103.831833 | 1.355737 | 20251202172807 |
| UPPER THOMSON MRT STATION | Exit 1 | 103.831916 | 1.354834 | 20251202172807 |
| UPPER THOMSON MRT STATION | Exit 5 | 103.832635 | 1.354418 | 20251202172807 |
| UPPER THOMSON MRT STATION | Exit 3 | 103.833925 | 1.354145 | 20251202172807 |

## How to use it

If the connector transport is working, the most useful way to use it is to ask focused location questions. For example, you could use **station lookup** to list all exits at a station, **nearest landmark lookup** to find the best exit for a destination, or **radius search** to see which exits fall within walking distance of an address.

| Goal | Example request |
| --- | --- |
| Find all exits at a station | "Show all exits for Bishan MRT" |
| Find one exit in detail | "Get exit detail for Orchard MRT Exit 2" |
| Find best exit for a landmark | "Which MRT exit is closest to Marina Bay Sands?" |
| Accessibility check | "Which accessible exits are near Plaza Singapura?" |
| Retail site analysis | "How many MRT exits are within 500 metres of Bugis Junction?" |
| Tourist guidance | "Which MRT exit should I use for Gardens by the Bay?" |

## Practical takeaway

The **data source is valid and current**, and the connector advertises a strong set of Singapore-navigation features. The main issue from this test is that the current connector session could not complete MCP calls successfully. If you want, I can next help you do one of two things: either troubleshoot the connector transport itself, or simulate specific feature outputs directly from the dataset for stations or landmarks you care about.
