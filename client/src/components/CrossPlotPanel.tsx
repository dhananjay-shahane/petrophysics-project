import { Card } from "@/components/ui/card";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function CrossPlotPanel() {
  // Sample data for cross plot
  const sampleData = [
    { x: 2.5, y: 15, name: 'Point 1' },
    { x: 3.0, y: 18, name: 'Point 2' },
    { x: 3.5, y: 22, name: 'Point 3' },
    { x: 4.0, y: 25, name: 'Point 4' },
    { x: 4.5, y: 28, name: 'Point 5' },
  ];

  return (
    <div className="h-full flex flex-col bg-background">
      <div className="flex-1 p-4">
        <Card className="h-full p-4">
          <div className="mb-4">
            <h3 className="text-lg font-semibold">Cross Plot</h3>
            <p className="text-sm text-muted-foreground">Visualize correlations between well log parameters</p>
          </div>
          
          <ResponsiveContainer width="100%" height="85%">
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                type="number" 
                dataKey="x" 
                name="Porosity" 
                unit="%" 
                label={{ value: 'Porosity (%)', position: 'bottom' }}
              />
              <YAxis 
                type="number" 
                dataKey="y" 
                name="Permeability" 
                unit="mD" 
                label={{ value: 'Permeability (mD)', angle: -90, position: 'left' }}
              />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Legend />
              <Scatter name="Well Data" data={sampleData} fill="#0ea5e9" />
            </ScatterChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </div>
  );
}
