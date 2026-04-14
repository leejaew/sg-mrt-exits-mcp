# sg-mrt-exits connector test

I tested the **sg-mrt-exits** connector from this environment. The connector itself is currently **not responding successfully** to MCP calls, but its public landing page is reachable and the underlying official MRT exit dataset can still be fetched and verified.

| Check | Outcome |
| --- | --- |
| Connector landing page | Reachable |
| MCP tool listing | Failed with `502` and `MCP server unavailable` |
| Server check | Failed with the same `502` response |
| Underlying MRT exit dataset | Successfully fetched |
| Confirmed exit records | 597 |

The connector page says it wraps the **LTA MRT Station Exit GeoJSON API** and exposes **15 structured tools** for Singapore MRT/LRT exit queries.

| Capability | Example tool |
| --- | --- |
| Find all exits for a station | `search_exits_by_station` |
| Get one exit’s details | `get_exit_detail` |
| Get map or directions links | `get_exit_map_view` |
| Find nearest exits by coordinates | `find_nearest_exit_by_coordinates` |
| Find nearest exits by landmark | `find_nearest_exit_by_landmark` |
| Find exits within a walking radius | `find_exits_within_radius` |
| View a station’s spatial footprint | `get_station_footprint` |
| List exits on an MRT/LRT line | `list_exits_by_line` |
| Check accessibility nearby | `accessibility_check` |
| Compare exits for a destination | `commuter_exit_comparison` |
| Tourist guidance to attractions | `tourist_guide_exits` |
| Retail site analysis | `retail_proximity_analysis` |
| Last-mile delivery planning | `logistics_delivery_planning` |
| Emergency response routing | `emergency_response_exits` |
| Urban density analysis | `urban_planning_exit_density` |

## Example ways to use it

If the connector is healthy, you would use it with location-focused requests such as the following.

| Goal | Example request |
| --- | --- |
| Station exits | "Show all exits for Bishan MRT" |
| Exact exit detail | "Get details for Orchard MRT Exit 2" |
| Best exit for a place | "Which MRT exit is closest to Marina Bay Sands?" |
| Nearby exits | "What exits are within 400 metres of Raffles Place?" |
| Accessibility | "Which accessible exits are near Plaza Singapura?" |
| Tourism | "Which MRT exit should I use for Gardens by the Bay?" |

## Sample data fetched

I successfully fetched real MRT-exit records from the official dataset behind the connector.

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

## Bottom line

The **data source is valid** and I was able to fetch real MRT-exit data, but the **live connector endpoint appears temporarily unavailable** from this session. If you want, I can next do either of these: simulate specific connector use cases from the dataset, or help troubleshoot the MCP endpoint itself.
