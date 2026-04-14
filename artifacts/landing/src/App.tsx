import { useState } from "react";

type Transport = "http" | "sse" | "stdio";

const TOOLS = [
  {
    name: "search_exits_by_station",
    tag: "station_name",
    description:
      "Search for all MRT exits belonging to a station by name. Supports full, partial, and wildcard searches — e.g. 'Orchard', '*hill', 'bishan*'.",
  },
  {
    name: "get_exit_detail",
    tag: "station_name · exit_code",
    description:
      "Get full details for a specific exit at a named station. Returns station name, exit code, coordinates, and the last-updated date.",
  },
  {
    name: "get_exit_map_view",
    tag: "station_name · exit_code",
    description:
      "Get the Google Maps view and directions links for a specific MRT exit. Use when the user explicitly requests a map view or directions.",
  },
  {
    name: "find_nearest_exit_by_coordinates",
    tag: "latitude · longitude · top_n",
    description:
      "Find the closest MRT exits to a given latitude and longitude. Fetches all exits and ranks by Haversine distance.",
  },
  {
    name: "find_nearest_exit_by_landmark",
    tag: "landmark_name · top_n",
    description:
      "Find the closest MRT exits to a named landmark or address in Singapore — e.g. 'Jewel Changi Airport', 'NUS', 'Marina Bay Sands'.",
  },
  {
    name: "find_exits_within_radius",
    tag: "radius_metres · latitude · longitude",
    description:
      "Find all MRT exits within a specified radius (in metres) of a location. Supply coordinates or a landmark name.",
  },
  {
    name: "get_station_footprint",
    tag: "station_name",
    description:
      "Get the complete spatial footprint of a station — all its exits with coordinates and a plain-text spread summary of the bounding box.",
  },
  {
    name: "list_exits_by_line",
    tag: "line_code",
    description:
      "List all MRT exits on a specific MRT/LRT line. Accepts a line code (e.g. 'TEL', 'NSL', 'CCL') or full line name. Exits are grouped by station.",
  },
  {
    name: "accessibility_check",
    tag: "latitude · longitude · radius_metres",
    description:
      "Identify MRT exits near a location and flag accessibility considerations, with links to LTA's official barrier-free access resources.",
  },
  {
    name: "commuter_exit_comparison",
    tag: "station_name · destination_landmark",
    description:
      "Compare all exits at a station to find which is closest to the commuter's actual destination within a neighbourhood.",
  },
  {
    name: "tourist_guide_exits",
    tag: "destination · include_map_links",
    description:
      "Help tourists find the best MRT exit for a Singapore attraction or landmark, with friendly walking distance descriptions.",
  },
  {
    name: "retail_proximity_analysis",
    tag: "radius_metres · landmark_name",
    description:
      "Analyse MRT exit density and proximity to assist with retail site selection, lease pricing context, or footfall estimation.",
  },
  {
    name: "logistics_delivery_planning",
    tag: "radius_metres · landmark_name",
    description:
      "Identify MRT exits near a delivery zone for last-mile logistics planning — courier pickup zones, delivery locker positioning.",
  },
  {
    name: "emergency_response_exits",
    tag: "top_n · latitude · longitude",
    description:
      "Find the nearest MRT exits to an incident location for emergency or first-responder use, with Google Maps directions links.",
  },
  {
    name: "urban_planning_exit_density",
    tag: "radius_metres · landmark_name",
    description:
      "Analyse MRT exit density across a defined area. Useful for urban planning, crowd modelling, or infrastructure assessment.",
  },
];

const TRANSPORT_CONFIGS: Record<Transport, string> = {
  http: `{
  "mcpServers": {
    "sg-mrt-exits": {
      "type": "streamableHttp",
      "url": "https://your-deployed-mcp-server.replit.app/mcp"
    }
  }
}`,
  sse: `{
  "mcpServers": {
    "sg-mrt-exits": {
      "transportType": "sse",
      "url": "https://your-deployed-mcp-server.replit.app/sse"
    }
  }
}`,
  stdio: `{
  "mcpServers": {
    "sg-mrt-exits": {
      "transportType": "stdio",
      "command": "python3",
      "args": ["/path/to/sg-mrt-exits-mcp/main.py"],
      "env": {
        "API_BASE_URL": "https://api.jael.ee",
        "API_USERNAME": "your-username",
        "API_TOKEN": "your-api-token"
      }
    }
  }
}`,
};

const TRANSPORT_HINTS: Record<Transport, React.ReactNode> = {
  http: (
    <>
      Paste this into Manus AI's custom MCP settings{" "}
      <span className="font-mono text-xs bg-gray-100 text-gray-600 px-1 py-0.5 rounded">
        Settings → MCP → Custom
      </span>
      . Replace the URL with your deployed MCP server endpoint.
    </>
  ),
  sse: (
    <>
      Paste this into Manus AI's custom MCP settings{" "}
      <span className="font-mono text-xs bg-gray-100 text-gray-600 px-1 py-0.5 rounded">
        Settings → MCP → Custom
      </span>
      . Replace the URL with your deployed SSE endpoint.{" "}
      Note: SSE is a legacy transport — prefer Streamable HTTP for new deployments.
    </>
  ),
  stdio: (
    <>
      Paste this into Manus AI's custom MCP settings or use with any stdio-compatible client. Replace{" "}
      <span className="font-mono text-xs bg-gray-100 text-gray-600 px-1 py-0.5 rounded">
        /path/to/
      </span>{" "}
      with the actual path and fill in your{" "}
      <span className="font-mono text-xs bg-gray-100 text-gray-600 px-1 py-0.5 rounded">
        API_USERNAME
      </span>{" "}
      and{" "}
      <span className="font-mono text-xs bg-gray-100 text-gray-600 px-1 py-0.5 rounded">
        API_TOKEN
      </span>{" "}
      for the api.jael.ee endpoint.
    </>
  ),
};

const TRANSPORT_LABELS: Record<Transport, string> = {
  http: "Streamable HTTP",
  sse: "SSE",
  stdio: "STDIO",
};

function SyntaxLine({ text }: { text: string }) {
  const parts: { text: string; cls: string }[] = [];
  let i = 0;
  while (i < text.length) {
    if (text[i] === '"') {
      const end = text.indexOf('"', i + 1);
      if (end === -1) { parts.push({ text: text.slice(i), cls: "text-[#98c379]" }); break; }
      const tok = text.slice(i, end + 1);
      const afterColon = text.slice(end + 1).trimStart().startsWith(":");
      parts.push({ text: tok, cls: afterColon ? "text-[#61afef]" : "text-[#98c379]" });
      i = end + 1;
    } else if (/[{}\[\],]/.test(text[i])) {
      parts.push({ text: text[i], cls: "text-[#e5c07b]" });
      i++;
    } else {
      let j = i;
      while (j < text.length && text[j] !== '"' && !/[{}\[\],]/.test(text[j])) j++;
      const chunk = text.slice(i, j);
      parts.push({ text: chunk, cls: "text-[#abb2bf]" });
      i = j;
    }
  }
  return (
    <span>
      {parts.map((p, idx) => (
        <span key={idx} className={p.cls}>{p.text}</span>
      ))}
    </span>
  );
}

function CodeBlock({ transport, onTransportChange }: { transport: Transport; onTransportChange: (t: Transport) => void }) {
  const [copied, setCopied] = useState(false);
  const config = TRANSPORT_CONFIGS[transport];

  const handleCopy = async () => {
    await navigator.clipboard.writeText(config);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const lines = config.split("\n");
  const transports: Transport[] = ["http", "sse", "stdio"];

  return (
    <div className="rounded-lg overflow-hidden border border-[#30363d]" style={{ background: "#0d1117" }}>
      <div className="flex items-center justify-between px-4 pt-3 pb-0 border-b border-[#30363d]">
        <div className="flex items-center gap-0">
          {transports.map((t) => (
            <button
              key={t}
              onClick={() => onTransportChange(t)}
              className={`text-xs font-mono px-3 py-2 border-b-2 transition-colors cursor-pointer ${
                transport === t
                  ? "border-[#f97316] text-[#f97316]"
                  : "border-transparent text-[#8b949e] hover:text-[#c9d1d9]"
              }`}
            >
              {TRANSPORT_LABELS[t]}
            </button>
          ))}
          <span className="text-[10px] text-[#4b5563] font-mono ml-3 mb-2 self-end">
            Manus AI · Custom MCP
          </span>
        </div>
        <button
          onClick={handleCopy}
          className="text-xs px-3 py-1 mb-2 rounded text-[#8b949e] border border-[#30363d] hover:border-[#f97316] hover:text-[#f97316] transition-colors cursor-pointer self-end"
        >
          {copied ? "Copied!" : "Copy"}
        </button>
      </div>
      <div className="p-4 overflow-x-auto">
        <pre className="text-sm font-mono leading-relaxed">
          {lines.map((line, i) => (
            <div key={i}>
              <SyntaxLine text={line} />
            </div>
          ))}
        </pre>
      </div>
    </div>
  );
}

function ToolCard({ tool, index }: { tool: typeof TOOLS[0]; index: number }) {
  return (
    <div
      className="rounded-lg px-5 py-4 flex gap-4 items-start border border-[#1e2433]"
      style={{ background: "#111827" }}
    >
      <span className="text-sm font-mono text-[#4b5563] mt-0.5 shrink-0 w-6 text-right">
        {String(index + 1).padStart(2, "0")}
      </span>
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2 mb-1.5">
          <span className="font-mono text-sm text-[#38bdf8] font-medium">{tool.name}</span>
          <span className="font-mono text-xs text-[#4b5563] bg-[#1f2937] px-2 py-0.5 rounded">
            {tool.tag}
          </span>
        </div>
        <p className="text-sm text-[#9ca3af] leading-relaxed">{tool.description}</p>
      </div>
    </div>
  );
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-xs font-bold tracking-[0.15em] uppercase mb-5" style={{ color: "#f97316" }}>
      {children}
    </h2>
  );
}

export default function App() {
  const [transport, setTransport] = useState<Transport>("http");

  return (
    <div className="min-h-screen bg-white text-gray-900">
      {/* Nav */}
      <header className="border-b border-gray-100 sticky top-0 bg-white/95 backdrop-blur-sm z-10">
        <div className="max-w-3xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl select-none" role="img" aria-label="MRT">🚇</span>
            <div>
              <div className="font-bold text-gray-900 leading-tight text-sm tracking-tight">
                sg-mrt-exits-mcp
              </div>
              <div className="text-[11px] text-gray-400 leading-tight hidden sm:block">
                Singapore LTA
                <span className="mx-1.5 text-orange-400">·</span>
                MRT Station Exits API
                <span className="mx-1.5 text-orange-400">·</span>
                MCP Server
              </div>
            </div>
          </div>
          <div className="flex items-center gap-1.5 bg-gray-900 text-gray-200 text-xs px-3 py-1.5 rounded-full font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-green-400 inline-block animate-pulse" />
            HTTP · SSE · STDIO · Manus AI
          </div>
        </div>
      </header>

      {/* Hero */}
      <main className="max-w-3xl mx-auto px-6 pt-12 pb-20">
        <h1 className="text-3xl font-bold text-gray-900 leading-snug mb-4">
          AI-ready access to Singapore's MRT station exits
        </h1>
        <p className="text-gray-600 leading-relaxed mb-12 text-base">
          This{" "}
          <span className="font-mono text-xs bg-gray-100 text-gray-700 px-1.5 py-0.5 rounded">
            MCP (Model Context Protocol)
          </span>{" "}
          server wraps the{" "}
          <strong className="text-gray-900">LTA MRT Station Exit GeoJSON API</strong> published at{" "}
          <strong className="text-gray-900">api.jael.ee</strong>. It exposes{" "}
          <strong className="text-gray-900">15 structured tools</strong> that Claude, Manus AI, and
          other MCP-compatible agents can call directly — covering navigation, spatial queries,
          accessibility, retail analytics, logistics, emergency response, and tourist guidance.
        </p>

        {/* Connect section */}
        <section className="mb-12">
          <SectionLabel>Connect your AI agent</SectionLabel>
          <CodeBlock transport={transport} onTransportChange={setTransport} />
          <p className="mt-3 text-sm text-gray-500">
            {TRANSPORT_HINTS[transport]}
          </p>
        </section>

        {/* Tools section */}
        <section>
          <SectionLabel>Available Tools ({TOOLS.length})</SectionLabel>
          <div className="flex flex-col gap-2">
            {TOOLS.map((tool, i) => (
              <ToolCard key={tool.name} tool={tool} index={i} />
            ))}
          </div>
        </section>

        {/* Footer */}
        <footer className="mt-16 pt-8 border-t border-gray-100 text-xs text-gray-400 flex flex-col gap-5">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
            <span className="font-mono">
              <a
                href="https://modelcontextprotocol.io"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-500 hover:text-orange-500 transition-colors underline underline-offset-2"
              >
                MCP Specification
              </a>
            </span>
          </div>
          <div className="border-t border-gray-100 pt-5 text-[11px] text-gray-400 leading-relaxed">
            <p>
              Land Transport Authority. (2019). LTA MRT Station Exit (GEOJSON) (2026) [Dataset]. data.gov.sg. Retrieved April 14, 2026 from{" "}
              <a
                href="https://data.gov.sg/datasets/d_b39d3a0871985372d7e1637193335da5/view"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-500 hover:text-orange-500 transition-colors underline underline-offset-2 break-all"
              >
                https://data.gov.sg/datasets/d_b39d3a0871985372d7e1637193335da5/view
              </a>
            </p>
            <p className="mt-1">
              Dataset license: Free forever for personal or commercial use, under the{" "}
              <a
                href="https://data.gov.sg/open-data-licence"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-500 hover:text-orange-500 transition-colors underline underline-offset-2"
              >
                Open Data Licence
              </a>
              .
            </p>
          </div>
        </footer>
      </main>
    </div>
  );
}
