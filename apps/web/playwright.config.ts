import path from "node:path";
import { defineConfig } from "@playwright/test";

const repoRoot = path.resolve(__dirname, "../..");

// Phone viewport 360x640 (CLAUDE.md). Starts the API (seeded with the fictional
// sample verdicts) and the built web app.
export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  fullyParallel: true,
  reporter: [["list"]],
  use: {
    baseURL: "http://localhost:3000",
    viewport: { width: 360, height: 640 },
    deviceScaleFactor: 2,
    isMobile: true,
    hasTouch: true,
  },
  projects: [{ name: "chromium", use: { browserName: "chromium" } }],
  webServer: [
    {
      command: "uv run uvicorn --app-dir services/api main:app --port 8000",
      cwd: repoRoot,
      url: "http://localhost:8000/health",
      reuseExistingServer: true,
      timeout: 60_000,
      env: {
        CONFAM_SEED_SAMPLES: "1",
        CONFAM_CORS_ORIGINS: "http://localhost:3000",
        CONFAM_RATE_LIMIT_PER_MINUTE: "1000",
      },
    },
    {
      command: "pnpm --filter web build && pnpm --filter web start -p 3000",
      cwd: repoRoot,
      url: "http://localhost:3000",
      reuseExistingServer: true,
      timeout: 240_000,
      env: { API_URL: "http://localhost:8000", NEXT_PUBLIC_API_URL: "http://localhost:8000", SHOW_SAMPLES: "1" },
    },
  ],
});
