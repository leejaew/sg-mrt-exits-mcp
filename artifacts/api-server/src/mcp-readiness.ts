import net from "net";
import { logger } from "./lib/logger";

let _ready = false;

export const isMcpReady = () => _ready;

function setReady(value: boolean) {
  if (_ready !== value) {
    _ready = value;
    if (value) {
      logger.info("MCP server is ready — proxy will now forward /mcp traffic");
    } else {
      logger.warn("MCP server connection lost — returning 503 until it recovers");
    }
  }
}

/**
 * Continuously poll TCP port 8000 to track Python FastMCP readiness.
 *
 * - On first successful connection  → set mcpReady = true
 * - If connection later fails again → set mcpReady = false and keep retrying
 * - Never gives up: runs for the entire lifetime of the Node.js process
 *
 * This means:
 *   • No matter how long Python takes to start (even 5+ minutes), MCP will
 *     eventually become available without a server restart.
 *   • If Python crashes and restarts, the proxy automatically recovers.
 */
export function watchMcpPort(
  port = 8000,
  host = "127.0.0.1",
  checkIntervalMs = 2000,
) {
  function tryConnect() {
    const sock = new net.Socket();
    sock.setTimeout(1500);

    sock
      .connect(port, host, () => {
        sock.destroy();
        setReady(true);
        // While ready, check less frequently (every 5 s) to detect crashes
        setTimeout(tryConnect, 5000);
      })
      .on("error", () => {
        sock.destroy();
        setReady(false);
        setTimeout(tryConnect, checkIntervalMs);
      })
      .on("timeout", () => {
        sock.destroy();
        setReady(false);
        setTimeout(tryConnect, checkIntervalMs);
      });
  }

  tryConnect();
}
