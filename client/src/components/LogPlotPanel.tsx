import { Card } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function LogPlotPanel() {
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
    <div className="h-full flex flex-col bg-background">
      <div className="flex-1 p-4">
        <Card className="h-full p-4">
          <div className="mb-4">
            <h3 className="text-lg font-semibold">Log Plot</h3>
            <p className="text-sm text-muted-foreground">Display well log data vs depth</p>
          </div>
          
          <ResponsiveContainer width="100%" height="85%">
            <LineChart data={sampleData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="gr" 
                label={{ value: 'Gamma Ray (API)', position: 'bottom' }}
              />
              <YAxis 
                dataKey="depth" 
                reversed
                label={{ value: 'Depth (m)', angle: -90, position: 'left' }}
              />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="gr" stroke="#8b5cf6" name="Gamma Ray" />
              <Line type="monotone" dataKey="resistivity" stroke="#0ea5e9" name="Resistivity" />
              <Line type="monotone" dataKey="porosity" stroke="#10b981" name="Porosity" />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </div>
  );
}
