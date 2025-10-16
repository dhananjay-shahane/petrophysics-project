import { useState, useEffect } from "react";
import { DndContext, DragEndEvent, DragStartEvent, DragOverlay, useSensor, useSensors, PointerSensor, DragOverEvent, useDroppable, useDraggable } from "@dnd-kit/core";
import MenuBar from "./MenuBar";
import ProjectInfoBar from "./ProjectInfoBar";
import ProjectListDialog from "./ProjectListDialog";
import DirectoryPicker from "./DirectoryPicker";
import NewWellDialog from "./NewWellDialog";
import WellsPanelNew from "./WellsPanelNew";
import ZonationPanelNew from "./ZonationPanelNew";
import DataBrowserPanelNew from "./DataBrowserPanelNew";
import FeedbackPanelNew from "./FeedbackPanelNew";
import WellLogPlotPanel from "./WellLogPlotPanel";
import CrossPlotPanel from "./CrossPlotPanel";
import LogPlotPanel from "./LogPlotPanel";
import { Resizable } from "re-resizable";
import BottomTaskbar from "./BottomTaskbar";
import { useToast } from "@/hooks/use-toast";
import { Layers, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";

type PanelId = "wells" | "zonation" | "dataBrowser" | "feedback" | "wellLogPlot" | "crossPlot" | "logPlot";

export interface WellData {
  id: string;
  name: string;
  path: string;
  data?: any;
  logs?: string[];
  metadata?: any;
}

export interface ProjectData {
  name: string;
  path: string;
  wells: WellData[];
  createdAt: string;
  updatedAt: string;
}

interface PanelState {
  visible: boolean;
  floating: boolean;
  minimized: boolean;
  position?: { x: number; y: number };
  size?: { width: number; height: number };
  dockZone?: "left" | "right" | "bottom" | "center";
}

interface DropZone {
  id: string;
  zone: "left" | "right" | "bottom" | "center";
  rect?: DOMRect;
}

const PANEL_COMPONENTS: Record<PanelId, any> = {
  wells: WellsPanelNew,
  zonation: ZonationPanelNew,
  dataBrowser: DataBrowserPanelNew,
  feedback: FeedbackPanelNew,
  wellLogPlot: WellLogPlotPanel,
  crossPlot: CrossPlotPanel,
  logPlot: LogPlotPanel,
};

const PANEL_TITLES: Record<PanelId, string> = {
  wells: "Wells",
  zonation: "Zonation",
  dataBrowser: "Data Browser",
  feedback: "Testing & Logs",
  wellLogPlot: "Well Log Plot",
  crossPlot: "Cross Plot",
  logPlot: "Log Plot",
};

function DraggableWrapper({ id, children }: { id: string; children: React.ReactNode }) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({ id });

  const style = transform ? {
    transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
  } : undefined;

  return (
    <div 
      ref={setNodeRef} 
      {...listeners} 
      {...attributes} 
      style={style}
      className={isDragging ? "opacity-50 cursor-move z-50" : ""}
    >
      {children}
    </div>
  );
}

function DropZone({ id, zone, isActive }: { id: string; zone: string; isActive: boolean }) {
  const { setNodeRef, isOver } = useDroppable({ id });

  const zoneStyles = {
    left: { left: 0, top: 0, bottom: 0, width: '25%' },
    right: { right: 0, top: 0, bottom: 0, width: '25%' },
    bottom: { left: 0, right: 0, bottom: 0, height: '25%' },
    center: { left: '25%', right: '25%', top: 0, bottom: '25%' },
  };

  return (
    <div
      ref={setNodeRef}
      style={zoneStyles[zone as keyof typeof zoneStyles]}
      className={`absolute border-2 border-dashed transition-all pointer-events-auto ${
        isActive && isOver
          ? "bg-primary/30 border-primary z-50"
          : isActive
          ? "bg-primary/10 border-primary/50 z-40"
          : "opacity-0 pointer-events-none"
      }`}
    >
      {isActive && isOver && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="bg-primary text-primary-foreground px-4 py-2 rounded font-semibold">
            Dock to {zone}
          </div>
        </div>
      )}
    </div>
  );
}

export default function AdvancedDockWorkspace() {
  const { toast } = useToast();
  const [panels, setPanels] = useState<Record<PanelId, PanelState>>({
    wells: { visible: true, floating: false, minimized: false, dockZone: "left" },
    zonation: { visible: true, floating: false, minimized: false, dockZone: "left" },
    dataBrowser: { visible: true, floating: false, minimized: false, dockZone: "right" },
    feedback: { visible: true, floating: false, minimized: false, dockZone: "bottom" },
    wellLogPlot: { visible: true, floating: false, minimized: false, dockZone: "center" },
    crossPlot: { visible: false, floating: false, minimized: false, dockZone: "center" },
    logPlot: { visible: false, floating: false, minimized: false, dockZone: "center" },
  });

  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [projectPath, setProjectPath] = useState<string>("");
  const [projectName, setProjectName] = useState<string>("");
  const [wells, setWells] = useState<WellData[]>([]);
  const [selectedWell, setSelectedWell] = useState<WellData | null>(null);
  const [projectCreatedAt, setProjectCreatedAt] = useState<string>("");
  const [draggedPanel, setDraggedPanel] = useState<PanelId | null>(null);
  const [projectListOpen, setProjectListOpen] = useState(false);
  const [directoryPickerOpen, setDirectoryPickerOpen] = useState(false);
  const [directoryPickerMode, setDirectoryPickerMode] = useState<"import" | "open">("open");
  const [newWellDialogOpen, setNewWellDialogOpen] = useState(false);
  const [dropZones, setDropZones] = useState<DropZone[]>([
    { id: "left", zone: "left" },
    { id: "right", zone: "right" },
    { id: "bottom", zone: "bottom" },
    { id: "center", zone: "center" },
  ]);
  const [leftPanelWidth, setLeftPanelWidth] = useState(280);
  const [rightPanelWidth, setRightPanelWidth] = useState(380);
  const [bottomPanelHeight, setBottomPanelHeight] = useState(200);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const [mobilePanelSelectorOpen, setMobilePanelSelectorOpen] = useState(false);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [theme]);

  // Load last opened project from localStorage on mount
  useEffect(() => {
    const savedProjectPath = localStorage.getItem('lastProjectPath');
    const savedProjectName = localStorage.getItem('lastProjectName');
    const savedProjectCreatedAt = localStorage.getItem('lastProjectCreatedAt');
    
    if (savedProjectPath) {
      setProjectPath(savedProjectPath);
      if (savedProjectName) {
        setProjectName(savedProjectName);
        (window as any).addAppLog?.(`📁 Opened project: ${savedProjectName}`, 'success', '📁');
      }
      if (savedProjectCreatedAt) {
        setProjectCreatedAt(savedProjectCreatedAt);
      }
    }
  }, []);

  // Save project path to localStorage and Flask session whenever it changes
  useEffect(() => {
    const saveProjectToSession = async () => {
      if (projectPath && projectPath !== "No path selected") {
        // Save to localStorage
        localStorage.setItem('lastProjectPath', projectPath);
        if (projectName) {
          localStorage.setItem('lastProjectName', projectName);
        }
        if (projectCreatedAt) {
          localStorage.setItem('lastProjectCreatedAt', projectCreatedAt);
        }
        
        // Save to Flask session
        try {
          await fetch('/api/session/project', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
              projectPath: projectPath,
              projectName: projectName,
              createdAt: projectCreatedAt
            })
          });
        } catch (error) {
          console.error('Error saving to session:', error);
        }
      }
    };
    
    saveProjectToSession();
  }, [projectPath, projectName, projectCreatedAt]);

  // Load wells when project path changes
  useEffect(() => {
    const loadWells = async () => {
      if (!projectPath || projectPath === "No path selected") {
        setWells([]);
        return;
      }

      try {
        const response = await fetch(`/api/wells/list?projectPath=${encodeURIComponent(projectPath)}`);
        if (response.ok) {
          const data = await response.json();
          if (data.wells && Array.isArray(data.wells)) {
            setWells(data.wells);
            (window as any).addAppLog?.(`🗂️ Loaded ${data.wells.length} well(s) from project`, 'success', '🗂️');
            
            // Auto-select first well if available
            if (data.wells.length > 0 && !selectedWell) {
              handleWellSelect(data.wells[0]);
            }
          }
        }
      } catch (error) {
        console.error('Error loading wells:', error);
        (window as any).addAppLog?.(`⚠️ Error loading wells: ${error}`, 'error', '⚠️');
      }
    };
    loadWells();
  }, [projectPath]);

  const togglePanel = (panelId: string) => {
    setPanels((prev) => {
      const panel = prev[panelId as PanelId];
      // If panel doesn't exist, create it with default values
      if (!panel) {
        return {
          ...prev,
          [panelId]: {
            visible: true,
            floating: false,
            minimized: false,
            dockZone: "center" as const,
          },
        };
      }
      // Otherwise toggle visibility
      return {
        ...prev,
        [panelId]: {
          ...panel,
          visible: !panel.visible,
        },
      };
    });
  };

  const closePanel = (panelId: PanelId) => {
    setPanels((prev) => ({
      ...prev,
      [panelId]: { ...prev[panelId], visible: false },
    }));
  };

  const dockPanel = (panelId: PanelId, zone?: "left" | "right" | "bottom" | "center") => {
    setPanels((prev) => ({
      ...prev,
      [panelId]: { ...prev[panelId], floating: false, dockZone: zone || prev[panelId].dockZone },
    }));
  };

  const floatPanel = (panelId: PanelId) => {
    setPanels((prev) => ({
      ...prev,
      [panelId]: { ...prev[panelId], floating: true },
    }));
  };

  const minimizePanel = (panelId: PanelId) => {
    setPanels((prev) => ({
      ...prev,
      [panelId]: { ...prev[panelId], minimized: true, visible: true },
    }));
  };

  const maximizePanel = (panelId: PanelId) => {
    setPanels((prev) => ({
      ...prev,
      [panelId]: { ...prev[panelId], minimized: false, visible: true },
    }));
  };

  const saveLayout = () => {
    const layoutData = { panels, theme, leftPanelWidth, rightPanelWidth, bottomPanelHeight };
    localStorage.setItem("dockLayout", JSON.stringify(layoutData));
  };

  const loadLayout = () => {
    const saved = localStorage.getItem("dockLayout");
    if (saved) {
      const layoutData = JSON.parse(saved);
      if (layoutData.panels) setPanels(layoutData.panels);
      if (layoutData.theme) setTheme(layoutData.theme);
      if (layoutData.leftPanelWidth) setLeftPanelWidth(layoutData.leftPanelWidth);
      if (layoutData.rightPanelWidth) setRightPanelWidth(layoutData.rightPanelWidth);
      if (layoutData.bottomPanelHeight) setBottomPanelHeight(layoutData.bottomPanelHeight);
    }
  };

  const saveProjectData = async () => {
    // Project save functionality disabled - API endpoint removed
    console.log('Project save disabled');
  };

  const loadProjectData = (projectData: ProjectData) => {
    setProjectName(projectData.name);
    setProjectPath(projectData.path);
    setWells(projectData.wells || []);
    setProjectCreatedAt(projectData.createdAt);
  };

  const handleProjectFolderSelect = (folderPath: string) => {
    setProjectPath(folderPath);
    const folderName = folderPath.split('/').pop() || folderPath;
    setProjectName(folderName);
    setProjectCreatedAt(new Date().toISOString());
    (window as any).addAppLog?.(`📁 Opened project: ${folderName}`, 'success', '📁');
  };

  const handleOpenImportPicker = () => {
    setDirectoryPickerMode("import");
    setDirectoryPickerOpen(true);
  };

  const handleOpenProjectPicker = () => {
    setDirectoryPickerMode("open");
    setDirectoryPickerOpen(true);
  };

  const handleDirectorySelect = (path: string) => {
    if (directoryPickerMode === "import") {
      (window as any).addAppLog?.(`📂 Import from directory: ${path}`, 'info', '📂');
      toast({
        title: "Import from Directory",
        description: `Selected directory: ${path}`,
      });
    } else {
      handleProjectFolderSelect(path);
      toast({
        title: "Project Opened",
        description: `Selected project directory: ${path}`,
      });
    }
  };

  const handleLoadProject = async (fileName: string) => {
    // Project load functionality disabled - API endpoint removed
    console.log('Project load disabled');
  };

  const updatePanelGeometry = (
    panelId: PanelId,
    position: { x: number; y: number },
    size: { width: number; height: number }
  ) => {
    setPanels((prev) => ({
      ...prev,
      [panelId]: { ...prev[panelId], position, size },
    }));
  };

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  const handleDragStart = (event: DragStartEvent) => {
    setDraggedPanel(event.active.id as PanelId);
  };

  const handleDragOver = (event: DragOverEvent) => {
  };

  const handleDragEnd = (event: DragEndEvent) => {
    setDraggedPanel(null);
    
    if (event.over) {
      const panelId = event.active.id as PanelId;
      const zone = event.over.id as "left" | "right" | "bottom" | "center";
      dockPanel(panelId, zone);
    }
  };

  const visiblePanels = new Set(
    Object.entries(panels)
      .filter(([_, state]) => state.visible)
      .map(([id]) => id)
  );

  const minimizedPanels = Object.entries(panels)
    .filter(([_, state]) => state.visible && state.minimized)
    .map(([id]) => ({ id, title: PANEL_TITLES[id as PanelId] }));

  const getDockedPanels = (zone: "left" | "right" | "bottom" | "center") => {
    return Object.entries(panels)
      .filter(([_, state]) => state.visible && !state.floating && !state.minimized && state.dockZone === zone)
      .map(([id]) => id as PanelId);
  };

  const parseCSVFile = async (file: File): Promise<any> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        try {
          const text = e.target?.result as string;
          const lines = text.split('\n').filter(line => line.trim());
          
          if (lines.length === 0) {
            resolve({ headers: [], rows: [] });
            return;
          }
          
          const headers = lines[0].split(',').map(h => h.trim());
          const rows = lines.slice(1).map(line => {
            const values = line.split(',').map(v => v.trim());
            return headers.reduce((obj, header, index) => {
              obj[header] = values[index] || '';
              return obj;
            }, {} as Record<string, string>);
          });
          
          resolve({ headers, rows, rowCount: rows.length });
        } catch (error) {
          reject(error);
        }
      };
      
      reader.onerror = () => reject(reader.error);
      reader.readAsText(file);
    });
  };

  const parseLASFile = async (file: File): Promise<any> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        try {
          const text = e.target?.result as string;
          const lines = text.split('\n');
          
          const wellInfo: Record<string, string> = {};
          let inWellSection = false;
          
          for (const line of lines) {
            const trimmedLine = line.trim();
            
            if (trimmedLine.startsWith('~W')) {
              inWellSection = true;
              continue;
            }
            
            if (trimmedLine.startsWith('~')) {
              inWellSection = false;
            }
            
            if (inWellSection && trimmedLine && !trimmedLine.startsWith('#')) {
              const colonIndex = trimmedLine.indexOf(':');
              if (colonIndex > 0) {
                const beforeColon = trimmedLine.substring(0, colonIndex).trim();
                const parts = beforeColon.split(/\s+/).filter(p => p.length > 0);
                
                if (parts.length >= 2) {
                  const mnemonicWithUnit = parts[0];
                  const mnemonic = mnemonicWithUnit.split('.')[0];
                  const value = parts[1];
                  wellInfo[mnemonic] = value;
                }
              }
            }
          }
          
          resolve({ 
            type: 'LAS',
            wellInfo,
            lineCount: lines.length 
          });
        } catch (error) {
          reject(error);
        }
      };
      
      reader.onerror = () => reject(reader.error);
      reader.readAsText(file);
    });
  };

  const handleLoadWells = async (files: File[], onError?: (message: string) => void) => {
    try {
      const newWells: WellData[] = [];
      
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const lowerName = file.name.toLowerCase();
        let parsedData;
        
        try {
          if (lowerName.endsWith('.csv')) {
            parsedData = await parseCSVFile(file);
          } else if (lowerName.endsWith('.las')) {
            parsedData = await parseLASFile(file);
          }
          
          newWells.push({
            id: `well-${Date.now()}-${i}`,
            name: file.name.replace(/\.(csv|las)$/i, ''),
            path: file.name,
            data: parsedData
          });
        } catch (fileError) {
          console.error(`Error parsing file ${file.name}:`, fileError);
          if (onError) {
            onError(`Failed to parse ${file.name}: ${fileError instanceof Error ? fileError.message : 'Unknown error'}`);
          }
        }
      }
      
      if (newWells.length > 0) {
        setWells(prev => [...prev, ...newWells]);
        
        if (!projectName) {
          const firstFileName = newWells[0].name;
          setProjectName(firstFileName);
        }
      }
    } catch (error) {
      console.error('Error loading wells:', error);
      if (onError) {
        onError(`Failed to load wells: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    }
  };

  const renderPanel = (panelId: PanelId, makeDraggable: boolean = false) => {
    const PanelComponent = PANEL_COMPONENTS[panelId];
    const panelState = panels[panelId];

    const commonProps = {
      onClose: () => closePanel(panelId),
      onMinimize: () => minimizePanel(panelId),
    };

    const panelSpecificProps = panelId === 'wells' 
      ? { wells, selectedWell, onWellSelect: handleWellSelect } 
      : panelId === 'feedback' 
      ? { onLoadWells: handleLoadWells, projectPath, selectedWell }
      : panelId === 'dataBrowser'
      ? { selectedWell }
      : panelId === 'wellLogPlot' || panelId === 'crossPlot' || panelId === 'logPlot'
      ? { selectedWell, projectPath }
      : {};

    if (panelState.floating) {
      return (
        <PanelComponent
          key={panelId}
          {...commonProps}
          {...panelSpecificProps}
          isFloating={true}
          onDock={() => dockPanel(panelId)}
          savedPosition={panelState.position}
          savedSize={panelState.size}
          onGeometryChange={(pos: any, size: any) => updatePanelGeometry(panelId, pos, size)}
        />
      );
    }

    const panel = (
      <PanelComponent
        key={panelId}
        {...commonProps}
        {...panelSpecificProps}
        onFloat={() => floatPanel(panelId)}
      />
    );

    if (makeDraggable) {
      return <DraggableWrapper id={panelId}>{panel}</DraggableWrapper>;
    }

    return panel;
  };

  const handleOpenNewWellDialog = () => {
    setNewWellDialogOpen(true);
  };

  const handleWellCreated = (well: { id: string; name: string; path: string }) => {
    setWells((prev) => [...prev, well]);
  };

  const handleWellSelect = async (well: WellData) => {
    setSelectedWell(well);
    
    // Close mobile sidebar when well is selected
    setIsMobileSidebarOpen(false);
    
    // If well data is not loaded yet, fetch it
    if (!well.data && well.path) {
      try {
        const response = await fetch(`/api/wells/load?filePath=${encodeURIComponent(well.path)}`);
        if (response.ok) {
          const wellData = await response.json();
          const updatedWell = { ...well, data: wellData.data, logs: wellData.logs, metadata: wellData.metadata };
          setSelectedWell(updatedWell);
          // Update the well in the list with the loaded data
          setWells(prev => prev.map(w => w.id === well.id ? updatedWell : w));
        }
      } catch (error) {
        console.error('Error loading well data:', error);
      }
    }
  };

  const leftPanels = getDockedPanels("left");
  const rightPanels = getDockedPanels("right");
  const bottomPanels = getDockedPanels("bottom");
  const centerPanels = getDockedPanels("center");

  return (
    <DndContext sensors={sensors} onDragStart={handleDragStart} onDragOver={handleDragOver} onDragEnd={handleDragEnd}>
      <div className="h-screen w-full flex flex-col bg-[#F0F4F5] dark:bg-background">
        {/* Sticky Menu Bar */}
        <div className="sticky top-0 z-50 bg-white dark:bg-card">
          <MenuBar
            onTogglePanel={togglePanel}
            visiblePanels={visiblePanels}
            onSaveLayout={saveLayout}
            onLoadLayout={loadLayout}
            theme={theme}
            onToggleTheme={toggleTheme}
            projectPath={projectPath}
            wellCount={wells.length}
            onProjectPathChange={handleProjectFolderSelect}
            onSaveProject={saveProjectData}
            onOpenProjectList={() => setProjectListOpen(true)}
            onOpenImportPicker={handleOpenImportPicker}
            onOpenProjectPicker={handleOpenProjectPicker}
            onNewWell={handleOpenNewWellDialog}
            onToggleMobileSidebar={() => setIsMobileSidebarOpen(!isMobileSidebarOpen)}
            isMobileSidebarOpen={isMobileSidebarOpen}
          />
          
          <ProjectInfoBar 
            projectPath={projectPath}
            projectName={projectName}
            wellCount={wells.length}
          />
        </div>

        <div className="flex-1 relative flex flex-col md:flex-row gap-1 p-1 h-full md:overflow-hidden">
          {draggedPanel && (
            <div className="hidden md:block">
              <DropZone id="left" zone="left" isActive={!!draggedPanel} />
              <DropZone id="right" zone="right" isActive={!!draggedPanel} />
              <DropZone id="bottom" zone="bottom" isActive={!!draggedPanel} />
              <DropZone id="center" zone="center" isActive={!!draggedPanel} />
            </div>
          )}
          {leftPanels.length > 0 && (
            <>
              {/* Mobile Sidebar Overlay */}
              {isMobileSidebarOpen && (
                <div 
                  className="fixed inset-0 bg-black/50 z-40 md:hidden"
                  onClick={() => setIsMobileSidebarOpen(false)}
                />
              )}
              
              {/* Desktop Sidebar - Hidden on mobile unless toggled */}
              <div className={`
                fixed md:relative inset-y-0 left-0 z-50 md:z-auto
                transform transition-transform duration-300 ease-in-out
                ${isMobileSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
                md:flex h-full
              `}>
                <Resizable
                  size={{ width: leftPanelWidth, height: "100%" }}
                  onResizeStop={(e, direction, ref, d) => {
                    setLeftPanelWidth(leftPanelWidth + d.width);
                  }}
                  enable={{ right: true }}
                  minWidth={200}
                  maxWidth={500}
                  className="flex flex-col gap-1 w-[280px] md:w-auto bg-background h-full relative"
                >
                  {/* Mobile Close Button inside sidebar */}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="absolute top-2 left-2 z-50 md:hidden h-8 w-8 bg-background/80 backdrop-blur-sm"
                    onClick={() => setIsMobileSidebarOpen(false)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                  
                  {leftPanels.map((panelId) => (
                    <div key={panelId} className="flex-1 min-h-0">
                      {renderPanel(panelId, true)}
                    </div>
                  ))}
                </Resizable>
              </div>
            </>
          )}

          <div className="flex-1 flex flex-col gap-1 w-full h-full min-h-0 overflow-auto md:overflow-hidden">
            {rightPanels.length > 0 || centerPanels.length > 0 ? (
              <div className="flex-1 flex flex-col md:flex-row gap-1 h-auto md:h-full md:min-h-0 min-h-[400px]">
                <div className="flex-1 bg-white dark:bg-card border border-card-border rounded overflow-hidden h-full min-h-[400px] md:min-h-0">
                  {centerPanels.length > 0 ? (
                    centerPanels.map((panelId) => <div key={panelId} className="h-full min-h-[400px] md:min-h-0">{renderPanel(panelId, true)}</div>)
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-muted-foreground text-sm px-2">
                      Central Workspace - Drag panels here
                    </div>
                  )}
                </div>

                {rightPanels.length > 0 && (
                  <div className="w-full md:w-auto h-full md:h-auto min-h-[300px]">
                    <Resizable
                      size={{ width: rightPanelWidth, height: "100%" }}
                      onResizeStop={(e, direction, ref, d) => {
                        setRightPanelWidth(rightPanelWidth + d.width);
                      }}
                      enable={{ left: true }}
                      minWidth={200}
                      maxWidth={600}
                      className="flex flex-col gap-1 w-full md:w-auto h-full min-h-[300px] md:min-h-0"
                    >
                      {rightPanels.map((panelId) => (
                        <div key={panelId} className="flex-1 min-h-[300px] md:min-h-0 h-full">
                          {renderPanel(panelId, true)}
                        </div>
                      ))}
                    </Resizable>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex-1 bg-white dark:bg-card border border-card-border rounded overflow-hidden flex items-center justify-center text-muted-foreground h-full">
                Central Workspace - Drag panels here
              </div>
            )}

            {bottomPanels.length > 0 && (
              <div className="w-full h-auto md:h-auto min-h-[250px] md:min-h-0">
                <Resizable
                  size={{ width: "100%", height: bottomPanelHeight }}
                  onResizeStop={(e, direction, ref, d) => {
                    setBottomPanelHeight(bottomPanelHeight + d.height);
                  }}
                  enable={{ top: true }}
                  minHeight={100}
                  maxHeight={400}
                  className="flex gap-1 w-full min-h-[250px] md:min-h-0"
                >
                  {bottomPanels.map((panelId) => (
                    <div key={panelId} className="flex-1 h-full min-h-[250px] md:min-h-0">
                      {renderPanel(panelId, true)}
                    </div>
                  ))}
                </Resizable>
              </div>
            )}
          </div>

          {Object.entries(panels).map(([id, state]) => 
            state.visible && state.floating && !state.minimized && renderPanel(id as PanelId)
          )}
        </div>

        <BottomTaskbar 
          minimizedPanels={minimizedPanels} 
          onMaximize={(id) => maximizePanel(id as PanelId)} 
        />

        {/* Mobile Panel Selector Button */}
        <Button
          className="fixed bottom-20 right-4 md:hidden z-40 h-14 w-14 rounded-full shadow-lg"
          onClick={() => setMobilePanelSelectorOpen(true)}
        >
          <Layers className="h-6 w-6" />
        </Button>

        {/* Mobile Panel Selector Sheet */}
        <Sheet open={mobilePanelSelectorOpen} onOpenChange={setMobilePanelSelectorOpen}>
          <SheetContent side="bottom" className="h-[60vh]">
            <SheetHeader>
              <SheetTitle>All Panels</SheetTitle>
              <SheetDescription>
                Select a panel to view
              </SheetDescription>
            </SheetHeader>
            <div className="grid grid-cols-2 gap-3 mt-6">
              {Object.entries(PANEL_TITLES).map(([id, title]) => (
                <Button
                  key={id}
                  variant={visiblePanels.has(id) ? "default" : "outline"}
                  className="h-20 flex flex-col items-center justify-center gap-2"
                  onClick={() => {
                    togglePanel(id as PanelId);
                    setMobilePanelSelectorOpen(false);
                  }}
                >
                  <span className="font-semibold">{title}</span>
                  {visiblePanels.has(id) && (
                    <span className="text-xs opacity-75">Active</span>
                  )}
                </Button>
              ))}
            </div>
          </SheetContent>
        </Sheet>

        <ProjectListDialog
          open={projectListOpen}
          onOpenChange={setProjectListOpen}
          onSelectProject={async (fileName) => {
            try {
              await handleLoadProject(fileName);
              toast({
                title: "Project Loaded",
                description: "Project data loaded successfully.",
              });
            } catch (error) {
              toast({
                title: "Load Failed",
                description: error instanceof Error ? error.message : "Failed to load project",
                variant: "destructive",
              });
              throw error;
            }
          }}
        />

        <DirectoryPicker
          open={directoryPickerOpen}
          onOpenChange={setDirectoryPickerOpen}
          onSelectPath={handleDirectorySelect}
          initialPath={projectPath}
          currentProjectPath={projectPath}
          onProjectDeleted={() => {
            setProjectPath("");
            setProjectName("");
            setWells([]);
            localStorage.removeItem('lastProjectPath');
            localStorage.removeItem('lastProjectName');
            localStorage.removeItem('lastProjectCreatedAt');
            toast({
              title: "Project Deleted",
              description: "The current project has been deleted. Please select a new project.",
            });
          }}
        />

        <NewWellDialog
          open={newWellDialogOpen}
          onOpenChange={setNewWellDialogOpen}
          projectPath={projectPath}
          onWellCreated={handleWellCreated}
        />
      </div>
    </DndContext>
  );
}
