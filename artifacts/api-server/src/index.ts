import { spawn } from "child_process";
import path from "path";
import app from "./app";
import { logger } from "./lib/logger";
import { watchMcpPort } from "./mcp-readiness";

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
// In development the "MRT Exits MCP Server" workflow runs Python separately.
// In production that workflow does not run, so we start it here as a subprocess.
if (process.env["NODE_ENV"] === "production") {
  const workspaceRoot = process.cwd();
  const mcpDir = path.join(workspaceRoot, "sg-mrt-exits-mcp");
  const mcpScript = path.join(mcpDir, "main.py");

  // Packages are pre-installed to this directory by the build step so that
  // Python can import them from the local filesystem without Nix hydration.
  const sitePackages = path.join(mcpDir, "site-packages");

  const mcpProcess = spawn("python3", [mcpScript], {
    env: {
      ...process.env,
      MCP_TRANSPORT: "streamable-http",
      // Bind Python on a fixed internal port; proxy targets this.
      PORT: "8000",
      FASTMCP_PORT: "8000",
      FASTMCP_HOST: "127.0.0.1",
      // Point Python to the pre-bundled packages so imports don't require Nix.
      PYTHONPATH: sitePackages,
    },
    stdio: "inherit",
    cwd: mcpDir,
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

  logger.info({ script: mcpScript, sitePackages }, "MCP server subprocess started");
}

// Watch port 8000 forever (dev + production).
// Sets mcpReady when Python is up, clears it if Python crashes, recovers on restart.
watchMcpPort(8000, "127.0.0.1", 2000);

// ── Start HTTP server ──────────────────────────────────────────────────────
app.listen(port, (err) => {
  if (err) {
    logger.error({ err }, "Error listening on port");
    process.exit(1);
  }

  logger.info({ port }, "Server listening");
});
