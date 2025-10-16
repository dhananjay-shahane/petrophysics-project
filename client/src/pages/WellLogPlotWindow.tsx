import { useLocation } from "wouter";
import WellLogPlot from "@/components/WellLogPlot";

export default function WellLogPlotWindow() {
  const [location] = useLocation();
  
  const params = new URLSearchParams(window.location.search);
  const wellId = params.get('wellId');
  const wellName = params.get('wellName');
  const projectPath = params.get('projectPath');

  const selectedWell = wellId && wellName ? {
    id: wellId,
    name: wellName,
    projectPath: projectPath || undefined
  } : null;

  return (
    <div className="h-screen w-full bg-background">
      <div className="h-full flex flex-col">
        <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-card">
          <h1 className="text-lg font-semibold text-foreground">
            Well Log Plot{wellName ? `: ${wellName}` : ''}
          </h1>
          <button
            onClick={() => window.close()}
            className="px-3 py-1 text-sm rounded hover:bg-accent text-muted-foreground hover:text-foreground"
          >
            Close Window
          </button>
        </div>
        <div className="flex-1 overflow-auto p-4">
          <WellLogPlot 
            selectedWell={selectedWell}
            projectPath={projectPath || undefined}
          />
        </div>
      </div>
    </div>
  );
}
