import { useState, useEffect } from "react";
import { DndContext, DragEndEvent, DragStartEvent, DragOverlay, useSensor, useSensors, PointerSensor, DragOverEvent, useDroppable, useDraggable } from "@dnd-kit/core";
import MenuBar from "./MenuBar";
import WellsPanelNew from "./WellsPanelNew";
import ZonationPanelNew from "./ZonationPanelNew";
import DataBrowserPanelNew from "./DataBrowserPanelNew";
import FeedbackPanelNew from "./FeedbackPanelNew";
import WellLogPlotPanel from "./WellLogPlotPanel";
import { Resizable } from "re-resizable";
import BottomTaskbar from "./BottomTaskbar";

type PanelId = "wells" | "zonation" | "dataBrowser" | "feedback" | "wellLogPlot";

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
};

const PANEL_TITLES: Record<PanelId, string> = {
  wells: "Wells",
  zonation: "Zonation",
  dataBrowser: "Data Browser",
  feedback: "Feedback",
  wellLogPlot: "Well Log Plot",
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
  const [panels, setPanels] = useState<Record<PanelId, PanelState>>({
    wells: { visible: true, floating: false, minimized: false, dockZone: "left" },
    zonation: { visible: true, floating: false, minimized: false, dockZone: "left" },
    dataBrowser: { visible: true, floating: false, minimized: false, dockZone: "right" },
    feedback: { visible: true, floating: false, minimized: false, dockZone: "bottom" },
    wellLogPlot: { visible: true, floating: false, minimized: false, dockZone: "center" },
  });

  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [projectPath, setProjectPath] = useState<string>("");
  const [wellCount, setWellCount] = useState<number>(0);
  const [draggedPanel, setDraggedPanel] = useState<PanelId | null>(null);
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
    setPanels((prev) => ({
      ...prev,
      [panelId]: {
        ...prev[panelId as PanelId],
        visible: !prev[panelId as PanelId].visible,
      },
    }));
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

  const renderPanel = (panelId: PanelId, makeDraggable: boolean = false) => {
    const PanelComponent = PANEL_COMPONENTS[panelId];
    const panelState = panels[panelId];

    if (panelState.floating) {
      return (
        <PanelComponent
          key={panelId}
          onClose={() => closePanel(panelId)}
          onMinimize={() => minimizePanel(panelId)}
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
        onClose={() => closePanel(panelId)}
        onMinimize={() => minimizePanel(panelId)}
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
          wellCount={wellCount}
          onProjectPathChange={setProjectPath}
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
      </div>
    </DndContext>
  );
}
