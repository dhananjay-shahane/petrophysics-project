import { useEffect, useState } from "react";
import type { WellData } from "./AdvancedDockWorkspace";

interface WellLogPlotProps {
  selectedWell?: WellData | null;
}

export default function WellLogPlot({ selectedWell }: WellLogPlotProps) {
  const [plotUrl, setPlotUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedWell) {
      setPlotUrl(null);
      setError(null);
      return;
    }

    if (!selectedWell.data || !Array.isArray(selectedWell.data) || selectedWell.data.length === 0) {
      setError("No well log data available");
      return;
    }

    const generatePlot = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const response = await fetch('/api/wells/generate-plot', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ wellPath: selectedWell.path })
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to generate plot');
        }
        
        const data = await response.json();
        
        if (data.success && data.plotUrl) {
          setPlotUrl(data.plotUrl);
        } else {
          throw new Error('No plot URL returned');
        }
      } catch (err: any) {
        console.error('Error generating plot:', err);
        setError(err.message || 'Failed to generate well log plot');
      } finally {
        setIsLoading(false);
      }
    };

    generatePlot();
  }, [selectedWell]);


  return (
    <div className="w-full h-full overflow-auto bg-white p-4 flex items-center justify-center">
      {!selectedWell ? (
        <div className="text-center text-muted-foreground">
          <p className="text-lg font-medium">No well selected</p>
          <p className="text-sm mt-2">Select a well from the Wells panel to display the log plot</p>
        </div>
      ) : isLoading ? (
        <div className="text-center text-muted-foreground">
          <p className="text-lg font-medium">Generating well log plot...</p>
          <p className="text-sm mt-2">{selectedWell.name}</p>
        </div>
      ) : error ? (
        <div className="text-center text-destructive">
          <p className="text-lg font-medium">Error generating plot</p>
          <p className="text-sm mt-2">{error}</p>
        </div>
      ) : plotUrl ? (
        <div className="w-full h-full flex flex-col">
          <div className="text-sm font-medium mb-2 text-center">{selectedWell.name}</div>
          <img 
            src={plotUrl} 
            alt={`Well log plot for ${selectedWell.name}`}
            className="max-w-full max-h-full object-contain mx-auto"
          />
        </div>
      ) : null}
    </div>
  );
}
