import { Router, type IRouter } from "express";
import { isMcpReady } from "../mcp-readiness";

const router: IRouter = Router();

router.get("/healthz", (_req, res) => {
  const mcpUp = isMcpReady();
  res.json({
    status: mcpUp ? "ok" : "degraded",
    mcp: mcpUp ? "up" : "starting",
  });
});

export default router;
