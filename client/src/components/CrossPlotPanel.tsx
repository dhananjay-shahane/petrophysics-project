import { useEffect, useState } from "react";
import DockablePanel from "./DockablePanel";
import type { WellData } from "./AdvancedDockWorkspace";

interface Dataset {
  name: string;
  type: string;
}

export default function CrossPlotPanel({ 
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
  const [plotImage, setPlotImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [availableLogs, setAvailableLogs] = useState<Dataset[]>([]);
  const [xLog, setXLog] = useState<string>('');
  const [yLog, setYLog] = useState<string>('');

  const generateCrossPlot = async (wellId: string, path: string, xLogName: string, yLogName: string) => {
    if (!xLogName || !yLogName) return;

    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/wells/${encodeURIComponent(wellId)}/cross-plot`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          projectPath: path,
          xLog: xLogName,
          yLog: yLogName
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to generate cross plot');
      }
      
      const data = await response.json();
      setPlotImage(data.image);
      
    } catch (err: any) {
      console.error('Error generating cross plot:', err);
      setError(err.message || 'Failed to generate cross plot');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!selectedWell) {
      setPlotImage(null);
      setError(null);
      setAvailableLogs([]);
      setXLog('');
      setYLog('');
      return;
    }

    const fetchAvailableLogs = async () => {
      try {
        const wellId = selectedWell.id || selectedWell.name;
        const path = projectPath || '';
        
        const response = await fetch(`/api/wells/datasets?projectPath=${encodeURIComponent(path)}&wellName=${encodeURIComponent(wellId)}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch datasets');
        }
        
        const data = await response.json();
        const logs = data.datasets?.filter((d: Dataset) => d.type === 'Cont' || d.type === 'continuous') || [];
        setAvailableLogs(logs);
        
        // Auto-select first two logs for cross plot
        if (logs.length >= 2) {
          const xLogName = logs[0].name;
          const yLogName = logs[1].name;
          setXLog(xLogName);
          setYLog(yLogName);
          
          // Auto-generate cross plot
          generateCrossPlot(wellId, path, xLogName, yLogName);
        } else if (logs.length === 1) {
          setXLog(logs[0].name);
        }
      } catch (err: any) {
        console.error('Error fetching datasets:', err);
        setError(err.message || 'Failed to fetch datasets');
      }
    };

    fetchAvailableLogs();
  }, [selectedWell, projectPath]);

  const handleLogChange = (axis: 'x' | 'y', logName: string) => {
    if (axis === 'x') {
      setXLog(logName);
      if (logName && yLog && selectedWell) {
        const wellId = selectedWell.id || selectedWell.name;
        const path = projectPath || '';
        generateCrossPlot(wellId, path, logName, yLog);
      }
    } else {
      setYLog(logName);
      if (xLog && logName && selectedWell) {
        const wellId = selectedWell.id || selectedWell.name;
        const path = projectPath || '';
        generateCrossPlot(wellId, path, xLog, logName);
      }
    }
  };

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
      <div className="w-full h-full flex flex-col bg-background">
        {/* Control Panel */}
        <div className="border-b p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">
              {selectedWell ? `Well: ${selectedWell.name}` : 'No well selected'}
            </h3>
          </div>
          
          {/* Axis Selection */}
          {availableLogs.length > 0 && (
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm text-muted-foreground">X-Axis Log:</label>
                <select
                  value={xLog}
                  onChange={(e) => handleLogChange('x', e.target.value)}
                  className="w-full px-3 py-2 text-sm border rounded-md bg-background"
                >
                  <option value="">Select log...</option>
                  {availableLogs.map((log) => (
                    <option key={log.name} value={log.name}>
                      {log.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm text-muted-foreground">Y-Axis Log:</label>
                <select
                  value={yLog}
                  onChange={(e) => handleLogChange('y', e.target.value)}
                  className="w-full px-3 py-2 text-sm border rounded-md bg-background"
                >
                  <option value="">Select log...</option>
                  {availableLogs.map((log) => (
                    <option key={log.name} value={log.name}>
                      {log.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}
        </div>

        {/* Plot Display Area */}
        <div className="flex-1 overflow-auto p-4">
          {!selectedWell ? (
            <div className="w-full h-full flex items-center justify-center">
              <div className="text-center text-muted-foreground">
                <p className="text-lg font-medium">No well selected</p>
                <p className="text-sm mt-2">Select a well from the Wells panel to display cross plot</p>
              </div>
            </div>
          ) : isLoading ? (
            <div className="w-full h-full flex items-center justify-center">
              <p className="text-muted-foreground">Generating cross plot...</p>
            </div>
          ) : error ? (
            <div className="w-full h-full flex items-center justify-center">
              <div className="text-center text-destructive">
                <p className="text-lg font-medium">Error</p>
                <p className="text-sm mt-2">{error}</p>
              </div>
            </div>
          ) : !xLog || !yLog ? (
            <div className="w-full h-full flex items-center justify-center">
              <p className="text-muted-foreground">Select X and Y axis logs to view the cross plot</p>
            </div>
          ) : plotImage ? (
            <div className="flex justify-center">
              <img 
                src={`data:image/png;base64,${plotImage}`} 
                alt="Cross Plot"
                className="max-w-full h-auto"
              />
            </div>
          ) : null}
        </div>
      </div>
    </DockablePanel>
  );
}
