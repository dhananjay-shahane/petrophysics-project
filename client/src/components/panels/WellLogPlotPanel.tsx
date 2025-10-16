import { useState } from "react";
import DockablePanel from "../workspace/DockablePanel";
import WellLogPlot from "../WellLogPlot";
import { ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import NewWindow from "react-new-window";
import type { WellData } from "../workspace/Workspace";

export default function WellLogPlotPanel({ 
  selectedWell,
  projectPath,
  selectedLogsForPlot,
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
  selectedLogsForPlot?: string[];
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

  const handleOpenInNewWindow = () => {
    if (!selectedWell) return;
    setIsNewWindowOpen(true);
  };

  const handleCloseNewWindow = () => {
    setIsNewWindowOpen(false);
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
        headerActions={
          <Button
            size="icon"
            variant="ghost"
            onClick={handleOpenInNewWindow}
            disabled={!selectedWell}
            className="h-6 w-6"
            title="Open in New Window"
          >
            <ExternalLink className="w-3.5 h-3.5" />
          </Button>
        }
      >
        <WellLogPlot selectedWell={selectedWell} projectPath={projectPath} initialSelectedLogs={selectedLogsForPlot} />
      </DockablePanel>

      {isNewWindowOpen && (
        <NewWindow
          title={`Well Log Plot - ${selectedWell?.name || 'No well selected'}`}
          onUnload={handleCloseNewWindow}
          features={{
            width: 1200,
            height: 800,
            left: (window.screen.width - 1200) / 2,
            top: (window.screen.height - 800) / 2
          }}
        >
          <div style={{ width: '100%', height: '100vh', overflow: 'auto' }}>
            <WellLogPlot selectedWell={selectedWell} projectPath={projectPath} initialSelectedLogs={selectedLogsForPlot} />
          </div>
        </NewWindow>
      )}
    </>
  );
}
