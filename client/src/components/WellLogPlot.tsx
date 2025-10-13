import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface Track {
  name: string;
  unit: string;
  description: string;
  data: number[];
  indexLog: number[];
  indexName: string;
}

interface LogPlotData {
  wellName: string;
  tracks: Track[];
  metadata?: any;
}

interface WellLogPlotProps {
  selectedWell?: { name: string; well_name?: string } | null;
}

export default function WellLogPlot({ selectedWell }: WellLogPlotProps) {
  const [plotData, setPlotData] = useState<LogPlotData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedWell) {
      setPlotData(null);
      setError(null);
      return;
    }

    const fetchPlotData = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const wellName = selectedWell.well_name || selectedWell.name;
        const response = await fetch(`/api/wells/${encodeURIComponent(wellName)}/log-plot`);
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to fetch plot data');
        }
        
        const data = await response.json();
        setPlotData(data);
        
        if ((window as any).addPythonLog) {
          (window as any).addPythonLog(`Loaded well log data for ${wellName}`, 'success');
        }
      } catch (err: any) {
        console.error('Error fetching plot data:', err);
        setError(err.message || 'Failed to load well log data');
        
        if ((window as any).addPythonLog) {
          (window as any).addPythonLog(`Error: ${err.message}`, 'error');
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchPlotData();
  }, [selectedWell]);

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

  if (isLoading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-background">
        <div className="text-center text-muted-foreground">
          <p className="text-lg font-medium">Loading well log data...</p>
          <p className="text-sm mt-2">{selectedWell.well_name || selectedWell.name}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-background">
        <div className="text-center text-destructive">
          <p className="text-lg font-medium">Error loading plot data</p>
          <p className="text-sm mt-2">{error}</p>
        </div>
      </div>
    );
  }

  if (!plotData || !plotData.tracks || plotData.tracks.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-background">
        <div className="text-center text-muted-foreground">
          <p className="text-lg font-medium">No log data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full overflow-auto bg-background p-4">
      <div className="text-lg font-semibold mb-4 text-center">{plotData.wellName}</div>
      <div className="flex gap-4 overflow-x-auto">
        {plotData.tracks.slice(0, 6).map((track, index) => {
          const chartData = track.data.map((value, i) => ({
            depth: track.indexLog[i],
            value: value
          })).filter(d => d.value !== null && !isNaN(d.value));

          const colors = ['#2563eb', '#9333ea', '#059669', '#dc2626', '#f59e0b', '#8b5cf6'];
          
          return (
            <div key={index} className="min-w-[200px] flex-shrink-0">
              <div className="text-sm font-medium text-center mb-2">
                {track.name}
                {track.unit && <span className="text-xs text-muted-foreground ml-1">({track.unit})</span>}
              </div>
              <ResponsiveContainer width={200} height={500}>
                <LineChart data={chartData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis 
                    dataKey="value" 
                    type="number" 
                    domain={['auto', 'auto']}
                    tick={{ fontSize: 10 }}
                  />
                  <YAxis 
                    dataKey="depth" 
                    reversed 
                    type="number"
                    domain={['auto', 'auto']}
                    tick={{ fontSize: 10 }}
                    label={{ value: track.indexName, angle: -90, position: 'insideLeft', style: { fontSize: 10 } }}
                  />
                  <Tooltip 
                    contentStyle={{ fontSize: 11, backgroundColor: '#1e293b', border: '1px solid #334155' }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke={colors[index % colors.length]} 
                    dot={false} 
                    strokeWidth={1.5}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          );
        })}
      </div>
    </div>
  );
}
