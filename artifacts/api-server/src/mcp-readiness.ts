import net from "net";
import { logger } from "./lib/logger";

let _ready = false;

export const isMcpReady = () => _ready;

export function setMcpReady() {
  _ready = true;
  logger.info("MCP server is ready — proxy will now forward /mcp traffic");
}

/**
 * Poll TCP port 8000 every `intervalMs` milliseconds until it accepts a
 * connection (Python FastMCP is up), then call setMcpReady().
 * Gives up after `timeoutMs` and logs a warning.
 */
export function waitForMcpPort(
  port = 8000,
  host = "127.0.0.1",
  intervalMs = 1000,
  timeoutMs = 120_000,
) {
  const deadline = Date.now() + timeoutMs;

  function tryConnect() {
    const sock = new net.Socket();
    sock.setTimeout(800);

    sock
      .connect(port, host, () => {
        sock.destroy();
        setMcpReady();
      })
      .on("error", () => {
        sock.destroy();
        if (Date.now() >= deadline) {
          logger.warn(
            { port, host },
            "Timed out waiting for MCP server — MCP proxy will remain disabled",
          );
          return;
        }
        setTimeout(tryConnect, intervalMs);
      })
      .on("timeout", () => {
        sock.destroy();
        if (Date.now() >= deadline) {
          logger.warn(
            { port, host },
            "Timed out waiting for MCP server — MCP proxy will remain disabled",
          );
          return;
        }
        setTimeout(tryConnect, intervalMs);
      });
  }

  tryConnect();
}
