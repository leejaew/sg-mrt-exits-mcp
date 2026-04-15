import express, { type Express } from "express";
import cors from "cors";
import pinoHttp from "pino-http";
import { createProxyMiddleware } from "http-proxy-middleware";
import type { ServerResponse } from "http";
import router from "./routes";
import { logger } from "./lib/logger";
import { isMcpReady } from "./mcp-readiness";

const app: Express = express();

app.use(
  pinoHttp({
    logger,
    serializers: {
      req(req) {
        return {
          id: req.id,
          method: req.method,
          url: req.url?.split("?")[0],
        };
      },
      res(res) {
        return {
          statusCode: res.statusCode,
        };
      },
    },
  }),
);
app.use(cors());

// ── MCP reverse proxy ──────────────────────────────────────────────────────
// Forwards /mcp, /sse, /messages, and /.well-known to the FastMCP Python
// server running on port 8000.  Registered BEFORE express.json() so the raw
// request body stream is not consumed before the proxy can forward it.
const mcpProxy = createProxyMiddleware({
  target: "http://127.0.0.1:8000",
  changeOrigin: true,
  on: {
    error(err, _req, res) {
      logger.warn({ err: (err as Error).message }, "MCP proxy error");
      const r = res as ServerResponse;
      if (!r.headersSent) {
        r.writeHead(502, { "Content-Type": "application/json" });
        r.end(
          JSON.stringify({
            error: "MCP server unavailable — please retry in a moment",
          }),
        );
      }
    },
  },
});

const MCP_PATH_PREFIXES = ["/mcp", "/sse", "/messages", "/.well-known"];

app.use((req, res, next) => {
  const p = req.path ?? "/";
  if (
    MCP_PATH_PREFIXES.some(
      (prefix) => p === prefix || p.startsWith(prefix + "/"),
    )
  ) {
    // Return 503 with Retry-After while Python is still starting up.
    // MCP clients that honour RFC 7231 will back off and retry automatically.
    if (!isMcpReady()) {
      res
        .status(503)
        .set("Retry-After", "5")
        .json({
          error:
            "MCP server is starting up — please retry in a few seconds",
          retryAfter: 5,
        });
      return;
    }
    return mcpProxy(req, res, next);
  }
  next();
});
// ── End MCP proxy ──────────────────────────────────────────────────────────

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use("/api", router);

export default app;
