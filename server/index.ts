import express, { type Request, Response, NextFunction } from "express";
import { registerRoutes } from "./routes";
import { setupVite, serveStatic, log } from "./vite";
import { spawn } from "child_process";
import axios from "axios";

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// Flask server configuration
const FLASK_PORT = 5001;
const FLASK_URL = `http://localhost:${FLASK_PORT}`;
let flaskProcess: any = null;

// Start Flask server
function startFlaskServer() {
  log("Starting Flask server...");
  flaskProcess = spawn("uv", ["run", "python", "server/run_flask.py"], {
    env: { ...process.env, FLASK_PORT: FLASK_PORT.toString() },
    stdio: "inherit"
  });

  flaskProcess.on("error", (error: Error) => {
    console.error("Failed to start Flask server:", error);
  });

  flaskProcess.on("exit", (code: number) => {
    if (code !== 0) {
      console.error(`Flask server exited with code ${code}`);
    }
  });
}

// Graceful shutdown
process.on("SIGINT", () => {
  if (flaskProcess) {
    flaskProcess.kill();
  }
  process.exit();
});

process.on("SIGTERM", () => {
  if (flaskProcess) {
    flaskProcess.kill();
  }
  process.exit();
});

app.use((req, res, next) => {
  const start = Date.now();
  const path = req.path;
  let capturedJsonResponse: Record<string, any> | undefined = undefined;

  const originalResJson = res.json;
  res.json = function (bodyJson, ...args) {
    capturedJsonResponse = bodyJson;
    return originalResJson.apply(res, [bodyJson, ...args]);
  };

  res.on("finish", () => {
    const duration = Date.now() - start;
    if (path.startsWith("/api")) {
      let logLine = `${req.method} ${path} ${res.statusCode} in ${duration}ms`;
      if (capturedJsonResponse) {
        logLine += ` :: ${JSON.stringify(capturedJsonResponse)}`;
      }

      if (logLine.length > 80) {
        logLine = logLine.slice(0, 79) + "…";
      }

      log(logLine);
    }
  });

  next();
});

(async () => {
  // Start Flask server
  startFlaskServer();
  
  // Wait for Flask to be ready
  await new Promise(resolve => setTimeout(resolve, 2000));

  // Serve static files from public directory FIRST (for well plots, etc.)
  app.use(express.static("public"));

  // Proxy API routes to Flask - must be before registerRoutes
  app.use('/api/*', async (req, res, next) => {
    // Routes to proxy to Flask
    const flaskPaths = [
      '/api/projects',
      '/api/wells/upload-las',
      '/api/wells/',
      '/api/visualization'
    ];
    
    // Check if this route should go to Flask
    const shouldProxy = flaskPaths.some(path => req.path.startsWith(path)) || 
                        req.path.match(/\/api\/wells\/[^/]+\/(log-plot|cross-plot)/);
    
    if (!shouldProxy) {
      return next(); // Let Express handle it
    }
    
    try {
      const flaskUrl = `${FLASK_URL}${req.path}`;
      const response = await axios({
        method: req.method,
        url: flaskUrl,
        data: req.body,
        params: req.query,
        headers: {
          'Content-Type': req.headers['content-type'] || 'application/json',
        },
        validateStatus: () => true
      });

      res.status(response.status).json(response.data);
    } catch (error: any) {
      console.error('Flask proxy error:', error.message);
      res.status(500).json({ error: 'Flask server error: ' + error.message });
    }
  });

  const server = await registerRoutes(app);

  app.use((err: any, _req: Request, res: Response, _next: NextFunction) => {
    const status = err.status || err.statusCode || 500;
    const message = err.message || "Internal Server Error";

    res.status(status).json({ message });
    throw err;
  });

  // importantly only setup vite in development and after
  // setting up all the other routes so the catch-all route
  // doesn't interfere with the other routes
  if (app.get("env") === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }

  // ALWAYS serve the app on the port specified in the environment variable PORT
  // Other ports are firewalled. Default to 5000 if not specified.
  // this serves both the API and the client.
  // It is the only port that is not firewalled.
  const port = parseInt(process.env.PORT || '5000', 10);
  server.listen({
    port,
    host: '0.0.0.0',
  }, () => {
    log(`serving on port ${port}`);
    log(`Flask server proxied from ${FLASK_URL}`);
  });
})();
