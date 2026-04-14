import { spawn } from "child_process";
import path from "path";
import app from "./app";
import { logger } from "./lib/logger";
import { waitForMcpPort } from "./mcp-readiness";

const rawPort = process.env["PORT"];

if (!rawPort) {
  throw new Error(
    "PORT environment variable is required but was not provided.",
  );
}

const port = Number(rawPort);

if (Number.isNaN(port) || port <= 0) {
  throw new Error(`Invalid PORT value: "${rawPort}"`);
}

// ── Spawn Python MCP server (production only) ──────────────────────────────
// In development the "MRT Exits MCP Server" workflow handles this separately.
// In production that workflow does not run, so we start it here as a subprocess
// so the proxy routes in app.ts have a target to forward to.
if (process.env["NODE_ENV"] === "production") {
  const mcpScript = path.join(process.cwd(), "sg-mrt-exits-mcp", "main.py");

  const mcpProcess = spawn("python3", [mcpScript], {
    env: {
      ...process.env,
      MCP_TRANSPORT: "streamable-http",
      // Bind Python on a fixed internal port; api-server proxy targets this.
      // Unset PORT so main.py reads FASTMCP_PORT instead (avoids confusion
      // with the Node PORT=8080 that gets spread from process.env).
      PORT: "8000",
      FASTMCP_PORT: "8000",
      FASTMCP_HOST: "127.0.0.1",
    },
    stdio: "inherit",
    cwd: path.join(process.cwd(), "sg-mrt-exits-mcp"),
  });

  mcpProcess.on("error", (err) => {
    logger.error({ err }, "Failed to start MCP server subprocess");
  });

  mcpProcess.on("exit", (code, signal) => {
    logger.warn({ code, signal }, "MCP server subprocess exited");
  });

  const cleanup = () => {
    mcpProcess.kill("SIGTERM");
  };
  process.once("exit", cleanup);
  process.once("SIGTERM", () => {
    cleanup();
    process.exit(0);
  });
  process.once("SIGINT", () => {
    cleanup();
    process.exit(0);
  });

  logger.info({ script: mcpScript }, "MCP server subprocess started");
}

// Poll port 8000 in the background (works in both dev and production).
// Sets the mcpReady flag so the proxy starts forwarding once Python is up.
waitForMcpPort(8000, "127.0.0.1", 1000, 180_000);

// ── Start HTTP server ──────────────────────────────────────────────────────
app.listen(port, (err) => {
  if (err) {
    logger.error({ err }, "Error listening on port");
    process.exit(1);
  }

  logger.info({ port }, "Server listening");
});
