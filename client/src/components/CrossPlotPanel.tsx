import DockablePanel from "./DockablePanel";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import type { WellData } from "./AdvancedDockWorkspace";

export default function CrossPlotPanel({ 
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
  // Prepare cross plot data from selected well
  let plotData: any[] = [];
  let xAxisLabel = "X Axis";
  let yAxisLabel = "Y Axis";
  
  if (selectedWell?.data && Array.isArray(selectedWell.data) && selectedWell.data.length > 0) {
    const logs = selectedWell.logs || [];
    // Use first two available numeric curves (excluding depth)
    const numericCurves = logs.filter((c: string) => c !== 'DEPT' && c !== 'DEPTH');
    
    if (numericCurves.length >= 2) {
      const xCurve = numericCurves[0];
      const yCurve = numericCurves[1];
      xAxisLabel = xCurve;
      yAxisLabel = yCurve;
      
      plotData = selectedWell.data.map((point: any, index: number) => ({
        x: point[xCurve],
        y: point[yCurve],
        name: `Point ${index + 1}`
      })).filter((p: any) => isFinite(p.x) && isFinite(p.y));
    }
  }

  return (
    <DockablePanel 
      id="crossPlot" 
      title="Cross Plot" 
      onClose={onClose}
      onMinimize={onMinimize}
      isFloating={isFloating}
      onDock={onDock}
      onFloat={onFloat}
      savedPosition={savedPosition}
      savedSize={savedSize}
      onGeometryChange={onGeometryChange}
      defaultSize={{ width: 800, height: 600 }}
    >
      <div className="h-full flex flex-col bg-background p-4">
        {!selectedWell ? (
          <div className="flex-1 flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <p className="text-lg">No well selected</p>
              <p className="text-sm mt-2">Select a well from the Wells panel to display cross plot</p>
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
            <ScatterChart margin={{ top: 20, right: 30, bottom: 40, left: 40 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                type="number" 
                dataKey="x" 
                name={xAxisLabel}
                label={{ value: xAxisLabel, position: 'bottom', offset: 0 }}
              />
              <YAxis 
                type="number" 
                dataKey="y" 
                name={yAxisLabel}
                label={{ value: yAxisLabel, angle: -90, position: 'insideLeft' }}
              />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Legend />
              <Scatter name={selectedWell.name} data={plotData} fill="#0ea5e9" />
            </ScatterChart>
          </ResponsiveContainer>
        )}
      </div>
    </DockablePanel>
  );
}
