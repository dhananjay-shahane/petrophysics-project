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
      const workspaceRoot = path.join(process.cwd(), "petrophysics-workplace");
      
      await fs.mkdir(workspaceRoot, { recursive: true });
      
      const dirPath = req.query.path as string || workspaceRoot;
      
      const resolvedPath = path.resolve(dirPath);
      const normalizedRoot = path.normalize(workspaceRoot + path.sep);
      const normalizedPath = path.normalize(resolvedPath + path.sep);
      
      if (!normalizedPath.startsWith(normalizedRoot)) {
        return res.status(403).json({ error: "Access denied: path outside petrophysics-workplace" });
      }
      
      try {
        const stats = await fs.stat(resolvedPath);
        if (!stats.isDirectory()) {
          return res.status(400).json({ error: "Path is not a directory" });
        }
      } catch (error: any) {
        if (error.code === 'ENOENT') {
          await fs.mkdir(workspaceRoot, { recursive: true });
          return res.json({
            currentPath: workspaceRoot,
            parentPath: workspaceRoot,
            directories: [],
            canGoUp: false,
          });
        }
        throw error;
      }

      const items = await fs.readdir(resolvedPath, { withFileTypes: true });
      
      const directories = items
        .filter(item => item.isDirectory() && !item.name.startsWith('.'))
        .map(item => ({
          name: item.name,
          path: path.join(resolvedPath, item.name),
        }))
        .sort((a, b) => a.name.localeCompare(b.name));

      const canGoUp = resolvedPath !== workspaceRoot;

      res.json({
        currentPath: resolvedPath,
        parentPath: canGoUp ? path.dirname(resolvedPath) : resolvedPath,
        directories,
        canGoUp,
      });
    } catch (error) {
      console.error("Error listing directories:", error);
      res.status(500).json({ error: "Failed to list directories" });
    }
  });

  app.post("/api/directories/create", async (req, res) => {
    try {
      const workspaceRoot = path.join(process.cwd(), "petrophysics-workplace");
      const { parentPath, folderName } = req.body;

      if (!folderName || !folderName.trim()) {
        return res.status(400).json({ error: "Folder name is required" });
      }

      const sanitizedName = folderName.trim();
      
      if (!/^[a-zA-Z0-9_-]+$/.test(sanitizedName)) {
        return res.status(400).json({ 
          error: "Folder name can only contain letters, numbers, hyphens, and underscores" 
        });
      }

      const resolvedParentPath = path.resolve(parentPath || workspaceRoot);
      const normalizedRoot = path.normalize(workspaceRoot + path.sep);
      const normalizedParent = path.normalize(resolvedParentPath + path.sep);
      
      if (!normalizedParent.startsWith(normalizedRoot)) {
        return res.status(403).json({ error: "Access denied: path outside petrophysics-workplace" });
      }

      const newFolderPath = path.join(resolvedParentPath, sanitizedName);
      
      try {
        await fs.access(newFolderPath);
        return res.status(400).json({ error: "Folder already exists" });
      } catch {
        // Folder doesn't exist, we can create it
      }

      await fs.mkdir(newFolderPath, { recursive: false });

      res.json({
        success: true,
        message: "Folder created successfully",
        path: newFolderPath,
        name: sanitizedName
      });
    } catch (error) {
      console.error("Error creating folder:", error);
      res.status(500).json({ error: "Failed to create folder" });
    }
  });

  app.delete("/api/directories/delete", async (req, res) => {
    try {
      const workspaceRoot = path.join(process.cwd(), "petrophysics-workplace");
      const { folderPath } = req.body;

      if (!folderPath || !folderPath.trim()) {
        return res.status(400).json({ error: "Folder path is required" });
      }

      const resolvedPath = path.resolve(folderPath);
      const normalizedRoot = path.normalize(workspaceRoot + path.sep);
      const normalizedPath = path.normalize(resolvedPath + path.sep);
      
      if (!normalizedPath.startsWith(normalizedRoot)) {
        return res.status(403).json({ error: "Access denied: path outside petrophysics-workplace" });
      }

      if (resolvedPath === workspaceRoot) {
        return res.status(403).json({ error: "Cannot delete workspace root" });
      }

      try {
        const stats = await fs.stat(resolvedPath);
        if (!stats.isDirectory()) {
          return res.status(400).json({ error: "Path is not a directory" });
        }
      } catch (error: any) {
        if (error.code === 'ENOENT') {
          return res.status(404).json({ error: "Folder not found" });
        }
        throw error;
      }

      await fs.rm(resolvedPath, { recursive: true, force: true });

      res.json({
        success: true,
        message: "Folder deleted successfully",
        path: resolvedPath
      });
    } catch (error) {
      console.error("Error deleting folder:", error);
      res.status(500).json({ error: "Failed to delete folder" });
    }
  });

  app.put("/api/directories/rename", async (req, res) => {
    try {
      const workspaceRoot = path.join(process.cwd(), "petrophysics-workplace");
      const { folderPath, newName } = req.body;

      if (!folderPath || !folderPath.trim()) {
        return res.status(400).json({ error: "Folder path is required" });
      }

      if (!newName || !newName.trim()) {
        return res.status(400).json({ error: "New folder name is required" });
      }

      const sanitizedName = newName.trim();
      
      if (!/^[a-zA-Z0-9_-]+$/.test(sanitizedName)) {
        return res.status(400).json({ 
          error: "Folder name can only contain letters, numbers, hyphens, and underscores" 
        });
      }

      const resolvedPath = path.resolve(folderPath);
      const normalizedRoot = path.normalize(workspaceRoot + path.sep);
      const normalizedPath = path.normalize(resolvedPath + path.sep);
      
      if (!normalizedPath.startsWith(normalizedRoot)) {
        return res.status(403).json({ error: "Access denied: path outside petrophysics-workplace" });
      }

      if (resolvedPath === workspaceRoot) {
        return res.status(403).json({ error: "Cannot rename workspace root" });
      }

      try {
        const stats = await fs.stat(resolvedPath);
        if (!stats.isDirectory()) {
          return res.status(400).json({ error: "Path is not a directory" });
        }
      } catch (error: any) {
        if (error.code === 'ENOENT') {
          return res.status(404).json({ error: "Folder not found" });
        }
        throw error;
      }

      const parentDir = path.dirname(resolvedPath);
      const newPath = path.join(parentDir, sanitizedName);

      try {
        await fs.access(newPath);
        return res.status(400).json({ error: "A folder with this name already exists" });
      } catch {
        // Folder doesn't exist, we can rename
      }

      await fs.rename(resolvedPath, newPath);

      res.json({
        success: true,
        message: "Folder renamed successfully",
        oldPath: resolvedPath,
        newPath: newPath,
        newName: sanitizedName
      });
    } catch (error) {
      console.error("Error renaming folder:", error);
      res.status(500).json({ error: "Failed to rename folder" });
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

  app.post("/api/projects/save", async (req, res) => {
    try {
      const { projectData } = req.body;

      if (!projectData || !projectData.name) {
        return res.status(400).json({ error: "Project data and name are required" });
      }

      const databaseDir = path.join(process.cwd(), "database");
      await fs.mkdir(databaseDir, { recursive: true });

      const fileName = `${projectData.name}_${Date.now()}.json`;
      const filePath = path.join(databaseDir, fileName);

      await fs.writeFile(filePath, JSON.stringify(projectData, null, 2), 'utf-8');

      res.json({
        success: true,
        message: "Project saved successfully",
        filePath: filePath,
        fileName: fileName
      });
    } catch (error) {
      console.error("Error saving project:", error);
      res.status(500).json({ error: "Failed to save project" });
    }
  });

  app.get("/api/projects/load/:fileName", async (req, res) => {
    try {
      const { fileName } = req.params;
      const databaseDir = path.join(process.cwd(), "database");
      const filePath = path.join(databaseDir, fileName);

      const data = await fs.readFile(filePath, 'utf-8');
      const projectData = JSON.parse(data);

      res.json({
        success: true,
        projectData: projectData
      });
    } catch (error) {
      console.error("Error loading project:", error);
      res.status(500).json({ error: "Failed to load project" });
    }
  });

  app.get("/api/projects/list", async (req, res) => {
    try {
      const databaseDir = path.join(process.cwd(), "database");
      
      try {
        await fs.access(databaseDir);
      } catch {
        await fs.mkdir(databaseDir, { recursive: true });
        return res.json({ success: true, projects: [] });
      }

      const files = await fs.readdir(databaseDir);
      const jsonFiles = files.filter(f => f.endsWith('.json'));

      const projects = await Promise.all(
        jsonFiles.map(async (file) => {
          try {
            const filePath = path.join(databaseDir, file);
            const stats = await fs.stat(filePath);
            const data = await fs.readFile(filePath, 'utf-8');
            const projectData = JSON.parse(data);
            return {
              fileName: file,
              name: projectData.name,
              path: projectData.path,
              wellCount: projectData.wells?.length || 0,
              createdAt: projectData.createdAt,
              updatedAt: projectData.updatedAt || stats.mtime.toISOString(),
            };
          } catch {
            return null;
          }
        })
      );

      res.json({
        success: true,
        projects: projects.filter(p => p !== null)
      });
    } catch (error) {
      console.error("Error listing projects:", error);
      res.status(500).json({ error: "Failed to list projects" });
    }
  });

  app.post("/api/wells/create", async (req, res) => {
    try {
      const { name, projectPath, description } = req.body;

      if (!name || !name.trim()) {
        return res.status(400).json({ error: "Well name is required" });
      }

      if (!projectPath || !projectPath.trim()) {
        return res.status(400).json({ error: "Project path is required" });
      }

      const wellName = name.trim();
      
      if (!/^[a-zA-Z0-9_-]+$/.test(wellName)) {
        return res.status(400).json({ 
          error: "Well name can only contain letters, numbers, hyphens, and underscores" 
        });
      }

      const wellsDir = path.join(projectPath, "10-WELLS");
      
      try {
        await fs.access(wellsDir);
      } catch {
        await fs.mkdir(wellsDir, { recursive: true });
      }

      const fileName = `${wellName}.json`;
      const filePath = path.join(wellsDir, fileName);

      try {
        await fs.access(filePath);
        return res.status(400).json({ error: "A well with this name already exists" });
      } catch {
        // File doesn't exist, we can create it
      }

      const wellData = {
        id: `well-${Date.now()}`,
        name: wellName,
        description: description || "",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        data: null,
        logs: [],
        metadata: {}
      };

      await fs.writeFile(filePath, JSON.stringify(wellData, null, 2), 'utf-8');

      res.json({
        success: true,
        message: `Well "${wellName}" created successfully`,
        filePath: filePath,
        well: wellData
      });
    } catch (error) {
      console.error("Error creating well:", error);
      res.status(500).json({ error: "Failed to create well" });
    }
  });

  const httpServer = createServer(app);

  return httpServer;
}
