# sg-mrt-exits Connector Test Report

I tested the **sg-mrt-exits** connector from the sandbox and verified that the server is configured, but the live endpoint was **not usable at the time of testing**. The CLI returned an authentication transport error with HTTP **421 `Invalid Host header`** when attempting both tool listing and server connectivity checks.

| Test step | Command pattern used | Observed result |
|---|---|---|
| List tools | `manus-mcp-cli tool list --server sg-mrt-exits` | Failed with HTTP 421 `Invalid Host header` |
| Server health/connectivity check | `manus-mcp-cli server check --server sg-mrt-exits` | Failed with the same HTTP 421 `Invalid Host header` |

Because of that connector-side issue, I could **not fetch live MRT exit records** in this run. So below I am giving you a practical brief of what the connector is designed to do, plus ready-to-use command patterns for when the endpoint is healthy again.

## Capability Brief

The connector is designed around Singapore **MRT/LRT station exits** and supports both simple lookup and more operational use cases.

| Capability | What it does | Example use case |
|---|---|---|
| Station exit lookup | Returns exits for a named station or station pattern | "Show all exits at Bugis" |
| Exit detail lookup | Returns structured details for one specific exit | Get address, coordinates, and links for a chosen exit |
| Map view | Returns a map-oriented view or map link for an exit | Open directions to an exit |
| Nearest exit by landmark | Resolves a named place and finds the closest MRT exit | "Which exit should I use for Marina Bay Sands?" |
| Nearest exit by coordinates | Finds the closest exit to a lat/lng pair | Mobile or logistics workflows |
| Exits within radius | Returns all exits within a specified distance | Site selection or nearby access checks |
| Line-wide listing | Lists exits grouped by MRT/LRT line and station | Network overview or planning |
| Station footprint | Describes the geographic spread of station exits | Accessibility and urban design review |
| Accessibility check | Identifies accessible exits near a place | Wheelchair-friendly navigation |
| Tourist guide lookup | Suggests which exit to use for attractions and POIs | Visitor directions |
| Retail proximity analysis | Measures exit density near a place | Footfall proxy for retail site analysis |
| Emergency response exits | Finds suitable nearby exits for response/evacuation | Incident handling |
| Logistics delivery planning | Finds practical exits near a delivery zone | Last-mile courier planning |
| Exit comparison | Compares exits at a station against a destination | "Which exit is closer to this mall?" |
| Urban density analysis | Measures exit coverage across an area | District-level planning |

## How to Use It

Below are practical command patterns you can run once the connector is responding normally.

### 1. List the available tools

```bash
manus-mcp-cli tool list --server sg-mrt-exits
```

### 2. Get all exits for a station

```bash
manus-mcp-cli tool call search_exits_by_station \
  --server sg-mrt-exits \
  --input '{"station_name":"Bugis"}'
```

### 3. Get details for one exit

This requires the connector's exit identifier from a previous lookup.

```bash
manus-mcp-cli tool call get_exit_detail \
  --server sg-mrt-exits \
  --input '{"exit_id":"BUGIS_EXIT_A"}'
```

### 4. Find the nearest exit to a landmark

```bash
manus-mcp-cli tool call find_nearest_exit_by_landmark \
  --server sg-mrt-exits \
  --input '{"landmark":"Marina Bay Sands"}'
```

### 5. Find all exits within a radius

```bash
manus-mcp-cli tool call find_exits_within_radius \
  --server sg-mrt-exits \
  --input '{"landmark":"Raffles Place","radius_meters":500}'
```

### 6. Check accessibility near a location

```bash
manus-mcp-cli tool call accessibility_check \
  --server sg-mrt-exits \
  --input '{"landmark":"Orchard Road"}'
```

### 7. Compare exits for a destination

```bash
manus-mcp-cli tool call commuter_exit_comparison \
  --server sg-mrt-exits \
  --input '{"station_name":"City Hall","destination":"Raffles City"}'
```

## Example Outputs You Should Expect

Since live data was unavailable, the examples below show the **shape of the output you should expect**, not real fetched records from this run.

| Feature | Expected output shape |
|---|---|
| `search_exits_by_station` | Station name, list of exit labels, possibly exit IDs, and map references |
| `get_exit_detail` | Exit ID, station name, exit label, coordinates, address, and map links |
| `find_nearest_exit_by_landmark` | Landmark, matched station/exit, walking relevance, coordinates, and distance |
| `find_exits_within_radius` | List of exits within the distance threshold, each with name and distance |
| `accessibility_check` | Accessible exits and supporting station/exit details |

## Bottom Line

The connector appears to be intended for **real-time structured Singapore MRT/LRT exit lookup and routing-oriented workflows**, and its feature surface is broad enough for navigation, tourism, accessibility, retail analysis, and operational planning. In this session, however, the live endpoint could not be used because of a connector-side HTTP **421 `Invalid Host header`** issue, so no live sample record could be retrieved.

If you want, the next sensible step is to **retry the connector later** or I can help you craft a **small test script** that exercises several commands automatically once the endpoint is healthy.
