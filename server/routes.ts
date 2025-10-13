import type { Express } from "express";
import { createServer, type Server } from "http";
import fs from "fs/promises";
import path from "path";

export async function registerRoutes(app: Express): Promise<Server> {
  // Directory Management Routes - for file browsing
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

  // Data Explorer Routes - for file preview
  app.get("/api/data/list", async (req, res) => {
    try {
      const workspaceRoot = path.join(process.cwd(), "petrophysics-workplace");
      const dirPath = req.query.path as string;
      
      if (!dirPath) {
        return res.status(400).json({ error: "Path is required" });
      }

      const resolvedPath = path.resolve(dirPath);
      const normalizedRoot = path.normalize(workspaceRoot + path.sep);
      const normalizedPath = path.normalize(resolvedPath + path.sep);
      
      if (!normalizedPath.startsWith(normalizedRoot)) {
        return res.status(403).json({ error: "Access denied: path outside petrophysics-workplace" });
      }

      const stats = await fs.stat(resolvedPath);
      if (!stats.isDirectory()) {
        return res.status(400).json({ error: "Path is not a directory" });
      }

      const items = await fs.readdir(resolvedPath, { withFileTypes: true });
      
      const fileItems = await Promise.all(items
        .filter(item => !item.name.startsWith('.'))
        .map(async (item) => {
          const itemPath = path.join(resolvedPath, item.name);
          const isDirectory = item.isDirectory();
          
          let hasFiles = false;
          if (isDirectory) {
            try {
              const subItems = await fs.readdir(itemPath, { withFileTypes: true });
              hasFiles = subItems.some(subItem => subItem.isFile());
            } catch {
              hasFiles = false;
            }
          }
          
          return {
            name: item.name,
            path: itemPath,
            type: isDirectory ? 'directory' : 'file',
            hasFiles: hasFiles
          };
        }));
      
      fileItems.sort((a, b) => {
        if (a.type === b.type) return a.name.localeCompare(b.name);
        return a.type === 'directory' ? -1 : 1;
      });

      const canGoUp = resolvedPath !== workspaceRoot;

      res.json({
        currentPath: resolvedPath,
        parentPath: canGoUp ? path.dirname(resolvedPath) : resolvedPath,
        items: fileItems,
        canGoUp,
      });
    } catch (error) {
      console.error("Error listing data:", error);
      res.status(500).json({ error: "Failed to list data" });
    }
  });

  app.get("/api/data/file", async (req, res) => {
    try {
      const workspaceRoot = path.join(process.cwd(), "petrophysics-workplace");
      const filePath = req.query.path as string;
      
      if (!filePath) {
        return res.status(400).json({ error: "File path is required" });
      }

      const resolvedPath = path.resolve(filePath);
      const normalizedRoot = path.normalize(workspaceRoot + path.sep);
      const normalizedPath = path.normalize(resolvedPath);
      
      if (!normalizedPath.startsWith(normalizedRoot)) {
        return res.status(403).json({ error: "Access denied: path outside petrophysics-workplace" });
      }

      const stats = await fs.stat(resolvedPath);
      if (!stats.isFile()) {
        return res.status(400).json({ error: "Path is not a file" });
      }

      const content = await fs.readFile(resolvedPath, 'utf-8');
      
      try {
        const jsonContent = JSON.parse(content);
        res.json({ content: jsonContent });
      } catch {
        res.json({ content: content });
      }
    } catch (error: any) {
      console.error("Error reading file:", error);
      res.status(500).json({ error: "Failed to read file: " + error.message });
    }
  });

  const httpServer = createServer(app);

  return httpServer;
}
