import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import fs from "fs/promises";
import path from "path";

export async function registerRoutes(app: Express): Promise<Server> {
  // put application routes here
  // prefix all routes with /api

  // use storage to perform CRUD operations on the storage interface
  // e.g. storage.insertUser(user) or storage.getUserByUsername(username)

  app.get("/api/directories/list", async (req, res) => {
    try {
      const dirPath = req.query.path as string || process.cwd();
      
      const resolvedPath = path.resolve(dirPath);
      
      const stats = await fs.stat(resolvedPath);
      if (!stats.isDirectory()) {
        return res.status(400).json({ error: "Path is not a directory" });
      }

      const items = await fs.readdir(resolvedPath, { withFileTypes: true });
      
      const directories = items
        .filter(item => item.isDirectory() && !item.name.startsWith('.'))
        .map(item => ({
          name: item.name,
          path: path.join(resolvedPath, item.name),
        }))
        .sort((a, b) => a.name.localeCompare(b.name));

      res.json({
        currentPath: resolvedPath,
        parentPath: path.dirname(resolvedPath),
        directories,
      });
    } catch (error) {
      console.error("Error listing directories:", error);
      res.status(500).json({ error: "Failed to list directories" });
    }
  });

  app.post("/api/projects/create", async (req, res) => {
    try {
      const { name, path: customPath } = req.body;

      if (!name || !name.trim()) {
        return res.status(400).json({ error: "Project name is required" });
      }

      if (!customPath || !customPath.trim()) {
        return res.status(400).json({ error: "Project path is required" });
      }

      const projectName = name.trim();
      const projectBasePath = customPath.trim();
      
      if (!/^[a-zA-Z0-9_-]+$/.test(projectName)) {
        return res.status(400).json({ 
          error: "Project name can only contain letters, numbers, hyphens, and underscores" 
        });
      }

      if (projectName.includes('..') || projectName.includes('/') || projectName.includes('\\')) {
        return res.status(400).json({ 
          error: "Invalid project name: path traversal characters not allowed" 
        });
      }

      const baseDir = path.join(projectBasePath, projectName);
      
      const resolvedPath = path.resolve(baseDir);
      if (resolvedPath.includes('..')) {
        return res.status(400).json({ 
          error: "Invalid path: path traversal not allowed" 
        });
      }

      const folders = [
        "01-OUTPUT",
        "02-INPUT_LAS_FOLDER",
        "03-DEVIATION",
        "04-WELL_HEADER",
        "05-TOPS_FOLDER",
        "06-ZONES_FOLDER",
        "07-DATA_EXPORTS",
        "08-VOL_MODELS",
        "09-SPECS",
        "10-WELLS"
      ];

      await fs.mkdir(baseDir, { recursive: true });

      for (const folder of folders) {
        await fs.mkdir(path.join(baseDir, folder), { recursive: true });
      }

      res.json({
        success: true,
        message: `Project "${projectName}" created successfully`,
        path: baseDir,
        folders: folders
      });
    } catch (error) {
      console.error("Error creating project:", error);
      res.status(500).json({ error: "Failed to create project" });
    }
  });

  const httpServer = createServer(app);

  return httpServer;
}
