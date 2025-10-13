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

  // Proxy ALL /api/wells/* routes to Flask (except /api/wells/load and /api/wells/create)
  app.use('/api/wells/*', async (req, res, next) => {
    // Skip these routes - they're handled by Express
    const expressRoutes = ['/api/wells/load', '/api/wells/create'];
    if (expressRoutes.some(route => req.path === route)) {
      return next();
    }
    
    try {
      // Construct full URL with query params
      const fullPath = req.originalUrl.replace(/^\/api/, ''); // Remove /api prefix to avoid double /api
      const flaskUrl = `${FLASK_URL}/api${fullPath}`;
      
      const response = await axios({
        method: req.method,
        url: flaskUrl,
        data: req.body,
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
  
  // Proxy other Flask routes
  app.use(['/api/projects/*', '/api/visualization/*'], async (req, res, next) => {
    try {
      const flaskUrl = `${FLASK_URL}${req.path}`;
      const queryString = Object.keys(req.query).length > 0 
        ? '?' + new URLSearchParams(req.query as any).toString()
        : '';
      
      const response = await axios({
        method: req.method,
        url: flaskUrl + queryString,
        data: req.body,
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
