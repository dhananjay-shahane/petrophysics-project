import { useState } from "react";
import DockablePanel from "./DockablePanel";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import type { WellData } from "./AdvancedDockWorkspace";
import { ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import NewWindow from "react-new-window";

export default function LogPlotPanel({ 
  selectedWell,
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

  // Prepare log plot data from selected well
  let plotData: any[] = [];
  let depthKey = "depth";
  const curvesToPlot: string[] = [];
  const colors = ["#8b5cf6", "#0ea5e9", "#10b981", "#f59e0b", "#ef4444"];
  
  if (selectedWell?.data && Array.isArray(selectedWell.data) && selectedWell.data.length > 0) {
    const logs = selectedWell.logs || [];
    depthKey = logs.find((c: string) => c === 'DEPT' || c === 'DEPTH') || 'DEPT';
    
    // Get up to 3 curves to plot (excluding depth)
    const availableCurves = logs.filter((c: string) => c !== 'DEPT' && c !== 'DEPTH').slice(0, 3);
    curvesToPlot.push(...availableCurves);
    
    plotData = selectedWell.data.filter((point: any) => isFinite(point[depthKey]));
  }

  const handleOpenInNewWindow = () => {
    if (!selectedWell) return;
    setIsNewWindowOpen(true);
  };

  const handleCloseNewWindow = () => {
    setIsNewWindowOpen(false);
  };

  const LogPlotContent = () => (
    <div className="h-full flex flex-col bg-background p-4">
      {!selectedWell ? (
        <div className="flex-1 flex items-center justify-center text-muted-foreground">
          <div className="text-center">
            <p className="text-lg">No well selected</p>
            <p className="text-sm mt-2">Select a well from the Wells panel to display log plot</p>
          </div>
        </div>
      ) : plotData.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-muted-foreground">
          <div className="text-center">
            <p className="text-lg">Loading well data...</p>
            <p className="text-sm mt-2">{selectedWell.name}</p>
          </div>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={plotData} margin={{ top: 20, right: 30, left: 40, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey={curvesToPlot[0] || "value"} 
              label={{ value: curvesToPlot[0] || 'Value', position: 'bottom', offset: 0 }}
            />
            <YAxis 
              dataKey={depthKey} 
              reversed
              label={{ value: 'Depth', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip />
            <Legend />
            {curvesToPlot.map((curve, index) => (
              <Line 
                key={curve}
                type="monotone" 
                dataKey={curve} 
                stroke={colors[index % colors.length]} 
                name={curve} 
                strokeWidth={2}
                dot={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );

  return (
    <>
      <DockablePanel 
        id="logPlot" 
        title="Log Plot" 
        onClose={onClose}
        onMinimize={onMinimize}
        isFloating={isFloating}
        onDock={onDock}
        onFloat={onFloat}
        savedPosition={savedPosition}
        savedSize={savedSize}
        onGeometryChange={onGeometryChange}
        defaultSize={{ width: 900, height: 600 }}
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
        <LogPlotContent />
      </DockablePanel>

      {isNewWindowOpen && (
        <NewWindow
          title={`Log Plot - ${selectedWell?.name || 'No well selected'}`}
          onUnload={handleCloseNewWindow}
          features={{
            width: 1200,
            height: 800,
            left: (window.screen.width - 1200) / 2,
            top: (window.screen.height - 800) / 2
          }}
        >
          <div style={{ width: '100%', height: '100vh', overflow: 'auto' }}>
            <LogPlotContent />
          </div>
        </NewWindow>
      )}
    </>
  );
}
