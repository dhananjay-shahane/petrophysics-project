import { useState, useEffect } from "react";
import { DndContext, DragEndEvent, DragStartEvent, DragOverlay, useSensor, useSensors, PointerSensor, DragOverEvent, useDroppable, useDraggable } from "@dnd-kit/core";
import MenuBar from "./MenuBar";
import ProjectInfoBar from "./ProjectInfoBar";
import ProjectListDialog from "./ProjectListDialog";
import DirectoryPicker from "./DirectoryPicker";
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

type PanelId = "wells" | "zonation" | "dataBrowser" | "feedback" | "wellLogPlot" | "crossPlot" | "logPlot";

export interface WellData {
  id: string;
  name: string;
  path: string;
  data?: any;
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
  feedback: "Feedback",
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
  const [projectCreatedAt, setProjectCreatedAt] = useState<string>("");
  const [draggedPanel, setDraggedPanel] = useState<PanelId | null>(null);
  const [projectListOpen, setProjectListOpen] = useState(false);
  const [directoryPickerOpen, setDirectoryPickerOpen] = useState(false);
  const [directoryPickerMode, setDirectoryPickerMode] = useState<"import" | "open">("open");
  const [dropZones, setDropZones] = useState<DropZone[]>([
    { id: "left", zone: "left" },
    { id: "right", zone: "right" },
    { id: "bottom", zone: "bottom" },
    { id: "center", zone: "center" },
  ]);
  const [leftPanelWidth, setLeftPanelWidth] = useState(280);
  const [rightPanelWidth, setRightPanelWidth] = useState(380);
  const [bottomPanelHeight, setBottomPanelHeight] = useState(200);

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
    const projectData: ProjectData = {
      name: projectName,
      path: projectPath,
      wells: wells,
      createdAt: projectCreatedAt || new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    try {
      const response = await fetch('/api/projects/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ projectData }),
      });

      const result = await response.json();
      
      if (!response.ok) {
        throw new Error(result.error || 'Failed to save project');
      }

      return result;
    } catch (error) {
      console.error('Error saving project:', error);
      throw error;
    }
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
    try {
      const response = await fetch(`/api/projects/load/${fileName}`);
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || 'Failed to load project');
      }

      if (result.success && result.projectData) {
        loadProjectData(result.projectData);
        return result;
      } else {
        throw new Error(result.error || 'Failed to load project');
      }
    } catch (error) {
      console.error('Error loading project:', error);
      throw error;
    }
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
      ? { wells } 
      : panelId === 'feedback' 
      ? { onLoadWells: handleLoadWells }
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

  const leftPanels = getDockedPanels("left");
  const rightPanels = getDockedPanels("right");
  const bottomPanels = getDockedPanels("bottom");
  const centerPanels = getDockedPanels("center");

  return (
    <DndContext sensors={sensors} onDragStart={handleDragStart} onDragOver={handleDragOver} onDragEnd={handleDragEnd}>
      <div className="h-screen w-full flex flex-col bg-[#F0F4F5] dark:bg-background overflow-hidden">
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
        />
        
        <ProjectInfoBar 
          projectPath={projectPath}
          projectName={projectName}
          wellCount={wells.length}
        />

        <div className="flex-1 relative flex gap-1 p-1">
          {draggedPanel && (
            <>
              <DropZone id="left" zone="left" isActive={!!draggedPanel} />
              <DropZone id="right" zone="right" isActive={!!draggedPanel} />
              <DropZone id="bottom" zone="bottom" isActive={!!draggedPanel} />
              <DropZone id="center" zone="center" isActive={!!draggedPanel} />
            </>
          )}
          {leftPanels.length > 0 && (
            <Resizable
              size={{ width: leftPanelWidth, height: "100%" }}
              onResizeStop={(e, direction, ref, d) => {
                setLeftPanelWidth(leftPanelWidth + d.width);
              }}
              enable={{ right: true }}
              minWidth={200}
              maxWidth={500}
              className="flex flex-col gap-1"
            >
              {leftPanels.map((panelId) => (
                <div key={panelId} className="flex-1">
                  {renderPanel(panelId, true)}
                </div>
              ))}
            </Resizable>
          )}

          <div className="flex-1 flex flex-col gap-1">
            {rightPanels.length > 0 || centerPanels.length > 0 ? (
              <div className="flex-1 flex gap-1">
                <div className="flex-1 bg-white dark:bg-card border border-card-border rounded overflow-hidden">
                  {centerPanels.length > 0 ? (
                    centerPanels.map((panelId) => <div key={panelId}>{renderPanel(panelId, true)}</div>)
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                      Central Workspace - Drag panels here
                    </div>
                  )}
                </div>

                {rightPanels.length > 0 && (
                  <Resizable
                    size={{ width: rightPanelWidth, height: "100%" }}
                    onResizeStop={(e, direction, ref, d) => {
                      setRightPanelWidth(rightPanelWidth + d.width);
                    }}
                    enable={{ left: true }}
                    minWidth={200}
                    maxWidth={600}
                    className="flex flex-col gap-1"
                  >
                    {rightPanels.map((panelId) => (
                      <div key={panelId} className="flex-1">
                        {renderPanel(panelId, true)}
                      </div>
                    ))}
                  </Resizable>
                )}
              </div>
            ) : (
              <div className="flex-1 bg-white dark:bg-card border border-card-border rounded overflow-hidden flex items-center justify-center text-muted-foreground">
                Central Workspace - Drag panels here
              </div>
            )}

            {bottomPanels.length > 0 && (
              <Resizable
                size={{ width: "100%", height: bottomPanelHeight }}
                onResizeStop={(e, direction, ref, d) => {
                  setBottomPanelHeight(bottomPanelHeight + d.height);
                }}
                enable={{ top: true }}
                minHeight={100}
                maxHeight={400}
                className="flex gap-1"
              >
                {bottomPanels.map((panelId) => (
                  <div key={panelId} className="flex-1">
                    {renderPanel(panelId, true)}
                  </div>
                ))}
              </Resizable>
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
        />
      </div>
    </DndContext>
  );
}
