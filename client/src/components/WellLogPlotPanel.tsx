import { useState } from "react";
import DockablePanel from "./DockablePanel";
import WellLogPlot from "./WellLogPlot";
import { ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import NewWindow from "react-new-window";
import type { WellData } from "./AdvancedDockWorkspace";

export default function WellLogPlotPanel({ 
  selectedWell,
  projectPath,
  onClose,
  onMinimize,
  isFloating,
  onDock,
  onFloat,
  savedPosition,
  savedSize,
  onGeometryChange
}: { 
  selectedWell?: WellData | null;
  projectPath?: string;
  onClose?: () => void;
  onMinimize?: () => void;
  isFloating?: boolean;
  onDock?: () => void;
  onFloat?: () => void;
  savedPosition?: { x: number; y: number };
  savedSize?: { width: number; height: number };
  onGeometryChange?: (pos: { x: number; y: number }, size: { width: number; height: number }) => void;
}) {
  const [isNewWindowOpen, setIsNewWindowOpen] = useState(false);
  const [windowWellData, setWindowWellData] = useState<WellData | null>(null);
  const [windowProjectPath, setWindowProjectPath] = useState<string>("");

  const handleOpenInNewWindow = () => {
    if (!selectedWell) return;
    
    setWindowWellData(selectedWell);
    setWindowProjectPath(projectPath || "");
    setIsNewWindowOpen(true);
  };

  const handleCloseNewWindow = () => {
    setIsNewWindowOpen(false);
    setWindowWellData(null);
    setWindowProjectPath("");
  };

  return (
    <>
      <DockablePanel 
        id="wellLogPlot" 
        title="Well Log Plot" 
        onClose={onClose}
        onMinimize={onMinimize}
        isFloating={isFloating}
        onDock={onDock}
        onFloat={onFloat}
        savedPosition={savedPosition}
        savedSize={savedSize}
        onGeometryChange={onGeometryChange}
        defaultSize={{ width: 1000, height: 700 }}
      >
        <div className="h-full flex flex-col">
          <div className="flex items-center justify-between px-3 py-2 border-b border-border bg-muted/30">
            <h3 className="text-sm font-medium text-foreground">
              {selectedWell?.name || 'No well selected'}
            </h3>
            <Button
              size="sm"
              variant="outline"
              onClick={handleOpenInNewWindow}
              disabled={!selectedWell}
              className="h-7 gap-1.5"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              Open in New Window
            </Button>
          </div>
          <div className="flex-1 overflow-auto">
            <WellLogPlot selectedWell={selectedWell} projectPath={projectPath} />
          </div>
        </div>
      </DockablePanel>

      {isNewWindowOpen && windowWellData && (
        <NewWindow
          title={`Well Log Plot - ${windowWellData.name}`}
          onUnload={handleCloseNewWindow}
          features={{
            width: 1200,
            height: 800,
            left: (window.screen.width - 1200) / 2,
            top: (window.screen.height - 800) / 2
          }}
        >
          <div style={{ width: '100%', height: '100vh', overflow: 'auto' }}>
            <WellLogPlot selectedWell={windowWellData} projectPath={windowProjectPath} />
          </div>
        </NewWindow>
      )}
    </>
  );
}
