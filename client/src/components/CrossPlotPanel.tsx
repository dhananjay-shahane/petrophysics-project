import DockablePanel from "./DockablePanel";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function CrossPlotPanel({ 
  onClose,
  onMinimize,
  isFloating,
  onDock,
  onFloat,
  savedPosition,
  savedSize,
  onGeometryChange
}: { 
  onClose?: () => void;
  onMinimize?: () => void;
  isFloating?: boolean;
  onDock?: () => void;
  onFloat?: () => void;
  savedPosition?: { x: number; y: number };
  savedSize?: { width: number; height: number };
  onGeometryChange?: (pos: { x: number; y: number }, size: { width: number; height: number }) => void;
}) {
  // Sample data for cross plot
  const sampleData = [
    { x: 2.5, y: 15, name: 'Point 1' },
    { x: 3.0, y: 18, name: 'Point 2' },
    { x: 3.5, y: 22, name: 'Point 3' },
    { x: 4.0, y: 25, name: 'Point 4' },
    { x: 4.5, y: 28, name: 'Point 5' },
  ];

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
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 30, bottom: 40, left: 40 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              type="number" 
              dataKey="x" 
              name="Porosity" 
              unit="%" 
              label={{ value: 'Porosity (%)', position: 'bottom', offset: 0 }}
            />
            <YAxis 
              type="number" 
              dataKey="y" 
              name="Permeability" 
              unit="mD" 
              label={{ value: 'Permeability (mD)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
            <Legend />
            <Scatter name="Well Data" data={sampleData} fill="#0ea5e9" />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </DockablePanel>
  );
}
