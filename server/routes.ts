import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import fs from "fs/promises";
import path from "path";
import multer from "multer";
import { parse } from "csv-parse/sync";
import { exec } from "child_process";
import { promisify } from "util";

const execPromise = promisify(exec);

// Helper function to parse LAS file and extract well information
function parseLASFile(lasContent: string): any {
  const lines = lasContent.split('\n');
  const wellInfo: any = {
    wellName: null,
    company: null,
    field: null,
    location: null,
    startDepth: null,
    stopDepth: null,
    step: null,
    nullValue: null,
    curveNames: [],
    curves: []
  };

  let currentSection = '';
  let headerMap: { [key: string]: number } = {};

  for (let line of lines) {
    line = line.trim();
    
    // Skip empty lines and comments
    if (!line || line.startsWith('#')) continue;

    // Detect sections
    if (line.startsWith('~')) {
      currentSection = line.toLowerCase();
      continue;
    }

    // Parse Well Information Section
    if (currentSection.includes('~well')) {
      const match = line.match(/^([A-Z]+)\s*\.([^:]*):(.*)$/i);
      if (match) {
        const mnem = match[1].toUpperCase();
        const value = match[3].trim();
        
        if (mnem === 'WELL') wellInfo.wellName = value;
        else if (mnem === 'COMP') wellInfo.company = value;
        else if (mnem === 'FLD') wellInfo.field = value;
        else if (mnem === 'LOC') wellInfo.location = value;
        else if (mnem === 'STRT') wellInfo.startDepth = parseFloat(value);
        else if (mnem === 'STOP') wellInfo.stopDepth = parseFloat(value);
        else if (mnem === 'STEP') wellInfo.step = parseFloat(value);
        else if (mnem === 'NULL') wellInfo.nullValue = parseFloat(value);
      }
    }

    // Parse Curve Information Section
    if (currentSection.includes('~curve')) {
      const match = line.match(/^([A-Z0-9_]+)\s*\./i);
      if (match) {
        const curveName = match[1].toUpperCase();
        wellInfo.curveNames.push(curveName);
      }
    }

    // Parse ASCII Data Section
    if (currentSection.includes('~ascii') || currentSection.includes('~a')) {
      // Skip if it's just the section header
      if (line.startsWith('~')) continue;
      
      const values = line.trim().split(/\s+/);
      if (values.length > 0 && !isNaN(parseFloat(values[0]))) {
        const dataPoint: any = {};
        wellInfo.curveNames.forEach((name: string, index: number) => {
          dataPoint[name] = values[index] ? parseFloat(values[index]) : null;
        });
        wellInfo.curves.push(dataPoint);
      }
    }
  }

  return wellInfo;
}

// Helper function to generate realistic LAS file content
function generateSampleLAS(wellName: string, record: any): string {
  // Parse and validate depth values
  let depthMin = 1000;
  let depthMax = 2000;
  
  if (record.depth_min) {
    const parsed = parseFloat(record.depth_min);
    if (isFinite(parsed)) {
      depthMin = parsed;
    }
  }
  
  if (record.depth_max) {
    const parsed = parseFloat(record.depth_max);
    if (isFinite(parsed)) {
      depthMax = parsed;
    }
  }
  
  // Ensure depth_max > depth_min
  if (depthMax <= depthMin) {
    depthMax = depthMin + 1000;
  }
  
  const location = record.location || "Unknown";
  
  let lasContent = `~Version Information
VERS.   2.0     : CWLS log ASCII Standard - VERSION 2.0
WRAP.   NO      : One line per depth step

~Well Information
#MNEM.UNIT  DATA                         DESCRIPTION
#---------  -----------------------------  -----------------------------------
STRT.M      ${depthMin}                   : START DEPTH
STOP.M      ${depthMax}                   : STOP DEPTH
STEP.M      0.5                           : STEP
NULL.       -999.25                       : NULL VALUE
COMP.       Sample Company                : COMPANY
WELL.       ${wellName}                   : WELL
FLD .       Sample Field                  : FIELD
LOC .       ${location}                   : LOCATION
CTRY.       USA                          : COUNTRY
SRVC.       Sample Service                : SERVICE COMPANY
DATE.       ${new Date().toISOString().split('T')[0]}  : LOG DATE

~Curve Information
#MNEM.UNIT      Curve Description
#---------      -----------------------------
DEPT.M          : Depth
GR  .GAPI       : Gamma Ray
NPHI.V/V        : Neutron Porosity
RHOB.G/C3       : Bulk Density
RT  .OHMM       : Deep Resistivity
PHIT.V/V        : Total Porosity
SW  .V/V        : Water Saturation

~Parameter Information
#MNEM.UNIT  VALUE       DESCRIPTION
#---------  ----------  -----------------------------
MUD .       WBM         : Mud Type
BHT .DEGC   85          : Bottom Hole Temperature
BS  .MM     215.9       : Bit Size
FD  .K/M3   1100        : Fluid Density

~ASCII
#DEPT    GR      NPHI    RHOB    RT      PHIT    SW
`;

  // Generate realistic well log data
  const numPoints = Math.floor((depthMax - depthMin) / 0.5) + 1;
  for (let i = 0; i < numPoints; i++) {
    const depth = depthMin + (i * 0.5);
    
    // Generate realistic petrophysical values with some variation
    const baseGR = 40 + Math.sin(i * 0.1) * 30 + Math.random() * 10;
    const baseNPHI = 0.20 + Math.sin(i * 0.15) * 0.05 + Math.random() * 0.02;
    const baseRHOB = 2.35 + Math.sin(i * 0.12) * 0.15 + Math.random() * 0.05;
    const baseRT = 10 + Math.sin(i * 0.08) * 20 + Math.random() * 5;
    const basePHIT = 0.18 + Math.sin(i * 0.14) * 0.04 + Math.random() * 0.02;
    const baseSW = 0.35 + Math.sin(i * 0.1) * 0.25 + Math.random() * 0.1;
    
    lasContent += `${depth.toFixed(2).padStart(8)}  ${baseGR.toFixed(2).padStart(7)}  ${baseNPHI.toFixed(4).padStart(7)}  ${baseRHOB.toFixed(3).padStart(7)}  ${baseRT.toFixed(2).padStart(7)}  ${basePHIT.toFixed(4).padStart(7)}  ${baseSW.toFixed(4).padStart(7)}\n`;
  }

  return lasContent;
}

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

  app.get("/api/wells/load", async (req, res) => {
    try {
      const filePath = req.query.filePath as string;
      
      if (!filePath) {
        return res.status(400).json({ error: "File path is required" });
      }
      
      const wellData = JSON.parse(await fs.readFile(filePath, 'utf-8'));
      res.json(wellData);
    } catch (error: any) {
      console.error("Error loading well data:", error);
      res.status(500).json({ error: "Failed to load well data: " + error.message });
    }
  });

  app.get("/api/wells/list", async (req, res) => {
    try {
      const projectPath = req.query.projectPath as string;
      
      if (!projectPath || !projectPath.trim()) {
        return res.status(400).json({ error: "Project path is required" });
      }

      // Security: Validate that the project path is within the workspace root
      const workspaceRoot = path.join(process.cwd(), "petrophysics-workplace");
      const resolvedProjectPath = path.resolve(projectPath);
      const normalizedRoot = path.normalize(workspaceRoot + path.sep);
      const normalizedProjectPath = path.normalize(resolvedProjectPath + path.sep);
      
      if (!normalizedProjectPath.startsWith(normalizedRoot)) {
        return res.status(403).json({ error: "Access denied: project path outside workspace" });
      }

      const wellsDir = path.join(resolvedProjectPath, "10-WELLS");
      
      // Check if wells directory exists
      try {
        await fs.access(wellsDir);
      } catch {
        // Wells directory doesn't exist, return empty array
        return res.json({
          success: true,
          wells: []
        });
      }

      const files = await fs.readdir(wellsDir);
      const jsonFiles = files.filter(f => f.endsWith('.json'));

      const wells = await Promise.all(
        jsonFiles.map(async (file) => {
          try {
            const filePath = path.join(wellsDir, file);
            const data = await fs.readFile(filePath, 'utf-8');
            const wellData = JSON.parse(data);
            return {
              id: wellData.id || file.replace('.json', ''),
              name: wellData.name || file.replace('.json', ''),
              path: filePath,
              data: wellData.data || null
            };
          } catch (error) {
            console.error(`Error reading well file ${file}:`, error);
            return null;
          }
        })
      );

      res.json({
        success: true,
        wells: wells.filter(w => w !== null)
      });
    } catch (error) {
      console.error("Error listing wells:", error);
      return res.json({
        success: true,
        wells: []
      });
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

  // Configure multer for CSV file uploads
  const upload = multer({ 
    storage: multer.memoryStorage(),
    limits: { fileSize: 10 * 1024 * 1024 } // 10MB limit
  });

  // Preview LAS file before uploading
  app.post("/api/wells/preview-las", async (req, res) => {
    try {
      const { lasContent } = req.body;
      
      if (!lasContent) {
        return res.status(400).json({ error: "No LAS content provided" });
      }

      const wellInfo = parseLASFile(lasContent);
      
      res.json({
        wellName: wellInfo.wellName,
        company: wellInfo.company,
        field: wellInfo.field,
        location: wellInfo.location,
        startDepth: wellInfo.startDepth,
        stopDepth: wellInfo.stopDepth,
        step: wellInfo.step,
        curveNames: wellInfo.curveNames,
        dataPoints: wellInfo.curves.length
      });
    } catch (error: any) {
      console.error("Error previewing LAS file:", error);
      res.status(500).json({ error: "Failed to preview LAS file: " + error.message });
    }
  });

  app.post("/api/wells/create-from-las", upload.single("lasFile"), async (req, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({ error: "No LAS file uploaded" });
      }

      const projectPath = req.body.projectPath;
      if (!projectPath || !projectPath.trim()) {
        return res.status(400).json({ error: "Project path is required" });
      }

      const wellsDir = path.join(projectPath, "10-WELLS");
      const lasDir = path.join(projectPath, "02-INPUT_LAS_FOLDER");
      
      // Create directories if they don't exist
      await fs.mkdir(wellsDir, { recursive: true });
      await fs.mkdir(lasDir, { recursive: true });

      // Parse LAS file content
      const lasContent = req.file.buffer.toString('utf-8');
      const lasFileName = req.file.originalname;
      
      // Extract well information from LAS file
      const wellInfo = parseLASFile(lasContent);
      
      if (!wellInfo.wellName) {
        return res.status(400).json({ error: "Could not extract well name from LAS file" });
      }

      // Sanitize well name
      let baseWellName = wellInfo.wellName.replace(/[^a-zA-Z0-9_-]/g, '_');
      
      if (!/^[a-zA-Z0-9_-]+$/.test(baseWellName)) {
        baseWellName = "WELL_" + Date.now();
      }

      // Find unique well name if one already exists
      let wellName = baseWellName;
      let fileName = `${wellName}.json`;
      let filePath = path.join(wellsDir, fileName);
      let counter = 1;

      while (true) {
        try {
          await fs.access(filePath);
          // File exists, try next number
          wellName = `${baseWellName}_${counter}`;
          fileName = `${wellName}.json`;
          filePath = path.join(wellsDir, fileName);
          counter++;
        } catch {
          // File doesn't exist, we can use this name
          break;
        }
      }

      // Create well data with parsed LAS information
      const wellData = {
        id: `well-${Date.now()}`,
        name: wellName,
        description: wellInfo.field || wellInfo.company || "",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        data: wellInfo.curves,
        logs: wellInfo.curveNames || [],
        metadata: {
          lasFile: lasFileName,
          depthMin: wellInfo.startDepth,
          depthMax: wellInfo.stopDepth,
          location: wellInfo.location || null,
          company: wellInfo.company || null,
          field: wellInfo.field || null,
          step: wellInfo.step || null,
          null: wellInfo.nullValue || null
        }
      };

      // Save well JSON file
      await fs.writeFile(filePath, JSON.stringify(wellData, null, 2), 'utf-8');

      // Copy LAS file to input folder
      const lasFilePath = path.join(lasDir, lasFileName);
      await fs.writeFile(lasFilePath, lasContent, 'utf-8');

      res.json({
        success: true,
        message: `Well "${wellName}" created successfully from LAS file`,
        filePath: filePath,
        well: wellData
      });
    } catch (error: any) {
      console.error("Error creating well from LAS file:", error);
      res.status(500).json({ error: "Failed to create well from LAS file: " + error.message });
    }
  });

  app.post("/api/wells/create-from-csv", upload.single("csvFile"), async (req, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({ error: "No CSV file uploaded" });
      }

      const projectPath = req.body.projectPath;
      if (!projectPath || !projectPath.trim()) {
        return res.status(400).json({ error: "Project path is required" });
      }

      // Parse CSV file
      const csvContent = req.file.buffer.toString('utf-8');
      const records = parse(csvContent, {
        columns: true,
        skip_empty_lines: true,
        trim: true
      });

      if (!Array.isArray(records) || records.length === 0) {
        return res.status(400).json({ error: "CSV file is empty or invalid" });
      }

      const wellsDir = path.join(projectPath, "10-WELLS");
      const lasDir = path.join(projectPath, "02-INPUT_LAS_FOLDER");
      
      // Create directories if they don't exist
      await fs.mkdir(wellsDir, { recursive: true });
      await fs.mkdir(lasDir, { recursive: true });

      const createdWells: any[] = [];
      const errors: string[] = [];

      for (let index = 0; index < records.length; index++) {
        const record = records[index] as any;
        try {
          const wellName = record.well_name?.trim();
          
          if (!wellName) {
            errors.push(`Row ${index + 1}: Missing well_name`);
            continue;
          }

          if (!/^[a-zA-Z0-9_-]+$/.test(wellName)) {
            errors.push(`Row ${index + 1}: Invalid well name "${wellName}" - only letters, numbers, hyphens, and underscores allowed`);
            continue;
          }

          const fileName = `${wellName}.json`;
          const filePath = path.join(wellsDir, fileName);

          // Check if well already exists
          try {
            await fs.access(filePath);
            errors.push(`Row ${index + 1}: Well "${wellName}" already exists`);
            continue;
          } catch {
            // File doesn't exist, we can create it
          }

          // Validate depth values
          let depthMin = null;
          let depthMax = null;
          
          if (record.depth_min) {
            const parsed = parseFloat(record.depth_min);
            if (!isFinite(parsed)) {
              errors.push(`Row ${index + 1}: Invalid depth_min value "${record.depth_min}"`);
              continue;
            }
            depthMin = parsed;
          }
          
          if (record.depth_max) {
            const parsed = parseFloat(record.depth_max);
            if (!isFinite(parsed)) {
              errors.push(`Row ${index + 1}: Invalid depth_max value "${record.depth_max}"`);
              continue;
            }
            depthMax = parsed;
          }
          
          // Check depth ordering if both are provided
          if (depthMin !== null && depthMax !== null && depthMax <= depthMin) {
            errors.push(`Row ${index + 1}: depth_max (${depthMax}) must be greater than depth_min (${depthMin})`);
            continue;
          }

          // Create well data with LAS information
          const wellData = {
            id: `well-${Date.now()}-${index}`,
            name: wellName,
            description: record.description?.trim() || "",
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            data: null,
            logs: [],
            metadata: {
              lasFile: record.las_file?.trim() || null,
              depthMin: depthMin,
              depthMax: depthMax,
              location: record.location?.trim() || null
            }
          };

          // If LAS file is specified, create a sample LAS file
          if (record.las_file?.trim()) {
            const lasFileName = record.las_file.trim();
            const lasFilePath = path.join(lasDir, lasFileName);
            
            // Generate sample LAS file content with realistic data
            const lasContent = generateSampleLAS(wellName, record);
            await fs.writeFile(lasFilePath, lasContent, 'utf-8');
          }

          await fs.writeFile(filePath, JSON.stringify(wellData, null, 2), 'utf-8');

          createdWells.push({
            id: wellData.id,
            name: wellData.name,
            path: filePath
          });
        } catch (error: any) {
          errors.push(`Row ${index + 1}: ${error.message}`);
        }
      }

      res.json({
        success: true,
        wellsCreated: createdWells.length,
        wells: createdWells,
        errors: errors.length > 0 ? errors : undefined,
        message: `Successfully created ${createdWells.length} well(s)${errors.length > 0 ? ` with ${errors.length} error(s)` : ''}`
      });
    } catch (error: any) {
      console.error("Error creating wells from CSV:", error);
      res.status(500).json({ error: "Failed to create wells from CSV: " + error.message });
    }
  });


  app.get("/api/data/list", async (req, res) => {
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
            items: [],
            canGoUp: false,
          });
        }
        throw error;
      }

      const items = await fs.readdir(resolvedPath, { withFileTypes: true });
      
      const fileItems = await Promise.all(items
        .filter(item => !item.name.startsWith('.'))
        .map(async item => {
          const itemPath = path.join(resolvedPath, item.name);
          let hasFiles = false;
          
          if (item.isDirectory()) {
            try {
              const dirContents = await fs.readdir(itemPath, { withFileTypes: true });
              hasFiles = dirContents.some(subItem => !subItem.name.startsWith('.'));
            } catch {
              hasFiles = false;
            }
          }
          
          return {
            name: item.name,
            path: itemPath,
            type: item.isDirectory() ? 'directory' as const : 'file' as const,
            hasFiles: item.isDirectory() ? hasFiles : undefined,
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

  // Well Management Endpoints using Python Flask backend
  app.post("/api/wells/upload-las", upload.single("file"), async (req, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({ error: "No file uploaded" });
      }

      const inputLasFolder = path.join(process.cwd(), 'petrophysics-workplace', '02-INPUT_LAS_FOLDER');
      await fs.mkdir(inputLasFolder, { recursive: true });

      const lasFilePath = path.join(inputLasFolder, req.file.originalname);
      await fs.writeFile(lasFilePath, req.file.buffer);

      // Call Python script to process LAS file
      const pythonScript = path.join(process.cwd(), 'server', 'python', 'process_las_file.py');
      const projectPath = path.join(process.cwd(), 'petrophysics-workplace');

      const { stdout } = await execPromise(
        `uv run python ${pythonScript} "${lasFilePath}" "${projectPath}"`
      );

      const result = JSON.parse(stdout);

      if (result.success) {
        res.json(result);
      } else {
        res.status(500).json({ error: result.error });
      }
    } catch (error: any) {
      console.error("Error uploading LAS file:", error);
      res.status(500).json({ error: "Failed to process LAS file: " + error.message });
    }
  });

  app.get("/api/wells/list", async (req, res) => {
    try {
      const wellsFolder = path.join(process.cwd(), 'petrophysics-workplace', '10-WELLS');
      await fs.mkdir(wellsFolder, { recursive: true });

      const files = await fs.readdir(wellsFolder);
      const wells = [];

      for (const file of files) {
        if (file.endsWith('.json')) {
          const filePath = path.join(wellsFolder, file);
          const content = await fs.readFile(filePath, 'utf-8');
          const well = JSON.parse(content);
          wells.push(well);
        }
      }

      res.json({ wells });
    } catch (error: any) {
      console.error("Error listing wells:", error);
      res.status(500).json({ error: "Failed to list wells: " + error.message });
    }
  });

  app.get("/api/wells/:wellName", async (req, res) => {
    try {
      const { wellName } = req.params;
      const wellsFolder = path.join(process.cwd(), 'petrophysics-workplace', '10-WELLS');
      const wellPath = path.join(wellsFolder, `${wellName}.json`);

      const content = await fs.readFile(wellPath, 'utf-8');
      const well = JSON.parse(content);

      res.json(well);
    } catch (error: any) {
      console.error("Error getting well:", error);
      res.status(404).json({ error: "Well not found" });
    }
  });

  // Well Log Plot Data Endpoint
  app.get("/api/wells/:wellName/log-plot", async (req, res) => {
    try {
      const { wellName } = req.params;
      const wellsFolder = path.join(process.cwd(), 'petrophysics-workplace', '10-WELLS');
      const wellPath = path.join(wellsFolder, `${wellName}.json`);

      const content = await fs.readFile(wellPath, 'utf-8');
      const well = JSON.parse(content);

      // Find the main dataset (not REFERENCE or WELL_HEADER)
      const mainDataset = well.datasets?.find((ds: any) => 
        ds.type !== 'REFERENCE' && ds.type !== 'WELL_HEADER'
      );

      if (!mainDataset) {
        return res.status(404).json({ error: "No log data found in well" });
      }

      const tracks = mainDataset.well_logs.map((log: any) => ({
        name: log.name,
        unit: log.unit,
        description: log.description,
        data: log.log,
        indexLog: mainDataset.index_log,
        indexName: mainDataset.index_name || 'DEPT'
      }));

      res.json({
        wellName: well.well_name,
        tracks,
        metadata: mainDataset.metadata
      });
    } catch (error: any) {
      console.error("Error generating log plot data:", error);
      res.status(500).json({ error: "Failed to generate log plot data: " + error.message });
    }
  });

  // Cross Plot Data Endpoint
  app.post("/api/wells/:wellName/cross-plot", async (req, res) => {
    try {
      const { wellName } = req.params;
      const { xCurve, yCurve, colorCurve } = req.body;

      if (!xCurve || !yCurve) {
        return res.status(400).json({ error: "xCurve and yCurve are required" });
      }

      const wellsFolder = path.join(process.cwd(), 'petrophysics-workplace', '10-WELLS');
      const wellPath = path.join(wellsFolder, `${wellName}.json`);

      const content = await fs.readFile(wellPath, 'utf-8');
      const well = JSON.parse(content);

      // Find the main dataset
      const mainDataset = well.datasets?.find((ds: any) => 
        ds.type !== 'REFERENCE' && ds.type !== 'WELL_HEADER'
      );

      if (!mainDataset) {
        return res.status(404).json({ error: "No log data found in well" });
      }

      // Find the requested curves
      const xLog = mainDataset.well_logs.find((log: any) => log.name === xCurve);
      const yLog = mainDataset.well_logs.find((log: any) => log.name === yCurve);
      const colorLog = colorCurve ? mainDataset.well_logs.find((log: any) => log.name === colorCurve) : null;

      if (!xLog || !yLog) {
        return res.status(404).json({ error: "Requested curves not found" });
      }

      // Combine data, filtering out null values
      const plotData = [];
      for (let i = 0; i < xLog.log.length; i++) {
        if (xLog.log[i] !== null && yLog.log[i] !== null) {
          const point: any = {
            x: xLog.log[i],
            y: yLog.log[i],
            depth: mainDataset.index_log[i]
          };
          if (colorLog && colorLog.log[i] !== null) {
            point.color = colorLog.log[i];
          }
          plotData.push(point);
        }
      }

      // Calculate correlation
      const xValues = plotData.map(p => p.x);
      const yValues = plotData.map(p => p.y);
      const correlation = calculateCorrelation(xValues, yValues);

      res.json({
        wellName: well.well_name,
        xCurve,
        yCurve,
        colorCurve,
        data: plotData,
        statistics: {
          numPoints: plotData.length,
          correlation,
          xRange: [Math.min(...xValues), Math.max(...xValues)],
          yRange: [Math.min(...yValues), Math.max(...yValues)]
        }
      });
    } catch (error: any) {
      console.error("Error generating cross plot data:", error);
      res.status(500).json({ error: "Failed to generate cross plot data: " + error.message });
    }
  });

  const httpServer = createServer(app);

  return httpServer;
}

// Helper function to calculate correlation coefficient
function calculateCorrelation(x: number[], y: number[]): number {
  const n = x.length;
  const sumX = x.reduce((a, b) => a + b, 0);
  const sumY = y.reduce((a, b) => a + b, 0);
  const sumXY = x.reduce((a, b, i) => a + b * y[i], 0);
  const sumX2 = x.reduce((a, b) => a + b * b, 0);
  const sumY2 = y.reduce((a, b) => a + b * b, 0);

  const numerator = n * sumXY - sumX * sumY;
  const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));

  return denominator === 0 ? 0 : numerator / denominator;
}
