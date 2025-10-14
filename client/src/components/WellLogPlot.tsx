import { useEffect, useState } from "react";

interface Dataset {
  name: string;
  type: string;
}

interface WellLogPlotProps {
  selectedWell?: { id?: string; name: string; well_name?: string; projectPath?: string } | null;
  projectPath?: string;
}

export default function WellLogPlot({ selectedWell, projectPath }: WellLogPlotProps) {
  const [plotImage, setPlotImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [availableLogs, setAvailableLogs] = useState<Dataset[]>([]);
  const [selectedLogs, setSelectedLogs] = useState<string[]>([]);

  const generatePlot = async (wellId: string, path: string, logNames: string[]) => {
    if (logNames.length === 0) return;

    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/wells/${encodeURIComponent(wellId)}/log-plot`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          projectPath: path,
          logNames: logNames
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to generate plot');
      }
      
      const data = await response.json();
      setPlotImage(data.image);
      
    } catch (err: any) {
      console.error('Error generating plot:', err);
      setError(err.message || 'Failed to generate plot');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    console.log('[WellLogPlot] useEffect triggered', { selectedWell, projectPath });
    
    if (!selectedWell) {
      setPlotImage(null);
      setError(null);
      setAvailableLogs([]);
      setSelectedLogs([]);
      return;
    }

    const fetchAvailableLogs = async () => {
      try {
        const wellId = selectedWell.id || selectedWell.well_name || selectedWell.name;
        const path = projectPath || selectedWell.projectPath || '';
        
        console.log('[WellLogPlot] Fetching datasets for well:', wellId, 'path:', path);
        
        const response = await fetch(`/api/wells/datasets?projectPath=${encodeURIComponent(path)}&wellName=${encodeURIComponent(wellId)}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch datasets');
        }
        
        const data = await response.json();
        console.log('[WellLogPlot] Datasets response:', data);
        
        const logs = data.datasets?.filter((d: Dataset) => d.type === 'Cont' || d.type === 'continuous') || [];
        console.log('[WellLogPlot] Continuous logs found:', logs.length, logs);
        setAvailableLogs(logs);
        
        // Auto-select first 3 logs and auto-generate plot
        if (logs.length > 0) {
          const logsToPlot = logs.slice(0, 3).map((l: Dataset) => l.name);
          setSelectedLogs(logsToPlot);
          
          console.log('[WellLogPlot] Auto-generating plot for logs:', logsToPlot);
          // Auto-generate plot
          generatePlot(wellId, path, logsToPlot);
        } else {
          console.log('[WellLogPlot] No continuous logs found, skipping plot generation');
        }
      } catch (err: any) {
        console.error('[WellLogPlot] Error fetching datasets:', err);
        setError(err.message || 'Failed to fetch datasets');
      }
    };

    fetchAvailableLogs();
  }, [selectedWell, projectPath]);

  const toggleLog = (logName: string) => {
    const newSelectedLogs = selectedLogs.includes(logName) 
      ? selectedLogs.filter(l => l !== logName)
      : [...selectedLogs, logName];
    
    setSelectedLogs(newSelectedLogs);
    
    // Auto-regenerate plot when logs change
    if (selectedWell && newSelectedLogs.length > 0) {
      const wellId = selectedWell.id || selectedWell.well_name || selectedWell.name;
      const path = projectPath || selectedWell.projectPath || '';
      generatePlot(wellId, path, newSelectedLogs);
    } else {
      setPlotImage(null);
    }
  };

  if (!selectedWell) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-background">
        <div className="text-center text-muted-foreground">
          <p className="text-lg font-medium">No well selected</p>
          <p className="text-sm mt-2">Select a well from the Wells panel to display the log plot</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full flex flex-col bg-background">
      {/* Control Panel */}
      <div className="border-b p-4 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold">Well: {selectedWell.well_name || selectedWell.name}</h3>
        </div>
        
        {/* Log Selection */}
        {availableLogs.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Select logs to plot:</p>
            <div className="flex flex-wrap gap-2">
              {availableLogs.map((log) => (
                <button
                  key={log.name}
                  onClick={() => toggleLog(log.name)}
                  className={`px-3 py-1 text-xs rounded-md border transition-colors ${
                    selectedLogs.includes(log.name)
                      ? 'bg-primary text-primary-foreground border-primary'
                      : 'bg-background hover:bg-accent border-border'
                  }`}
                >
                  {log.name}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Plot Display Area */}
      <div className="flex-1 overflow-auto p-4">
        {isLoading && (
          <div className="w-full h-full flex items-center justify-center">
            <p className="text-muted-foreground">Generating plot...</p>
          </div>
        )}

        {error && (
          <div className="w-full h-full flex items-center justify-center">
            <div className="text-center text-destructive">
              <p className="text-lg font-medium">Error</p>
              <p className="text-sm mt-2">{error}</p>
            </div>
          </div>
        )}

        {!isLoading && !error && !plotImage && selectedLogs.length === 0 && (
          <div className="w-full h-full flex items-center justify-center">
            <p className="text-muted-foreground">Select at least one log to view the plot</p>
          </div>
        )}

        {!isLoading && plotImage && (
          <div className="flex justify-center">
            <img 
              src={`data:image/png;base64,${plotImage}`} 
              alt="Well Log Plot"
              className="max-w-full h-auto"
            />
          </div>
        )}
      </div>
    </div>
  );
}
