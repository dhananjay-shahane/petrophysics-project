import DockablePanel from "./DockablePanel";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function LogPlotPanel({ 
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
  // Sample data for log plot
  const sampleData = [
    { depth: 1000, gr: 45, resistivity: 2.5, porosity: 18 },
    { depth: 1010, gr: 50, resistivity: 3.0, porosity: 20 },
    { depth: 1020, gr: 60, resistivity: 4.5, porosity: 22 },
    { depth: 1030, gr: 55, resistivity: 3.8, porosity: 19 },
    { depth: 1040, gr: 48, resistivity: 2.8, porosity: 17 },
    { depth: 1050, gr: 52, resistivity: 3.2, porosity: 21 },
  ];

  return (
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
    >
      <div className="h-full flex flex-col bg-background p-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={sampleData} margin={{ top: 20, right: 30, left: 40, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="gr" 
              label={{ value: 'Gamma Ray (API)', position: 'bottom', offset: 0 }}
            />
            <YAxis 
              dataKey="depth" 
              reversed
              label={{ value: 'Depth (m)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="gr" stroke="#8b5cf6" name="Gamma Ray" strokeWidth={2} />
            <Line type="monotone" dataKey="resistivity" stroke="#0ea5e9" name="Resistivity" strokeWidth={2} />
            <Line type="monotone" dataKey="porosity" stroke="#10b981" name="Porosity" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </DockablePanel>
  );
}
