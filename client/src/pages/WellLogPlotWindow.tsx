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
    <div className="h-screen w-full bg-background overflow-hidden">
      <div className="h-full flex flex-col">
        <div className="flex items-center justify-between px-2 sm:px-4 py-2 border-b border-border bg-card shrink-0">
          <h1 className="text-sm sm:text-lg font-semibold text-foreground truncate">
            Well Log Plot{wellName ? `: ${wellName}` : ''}
          </h1>
          <button
            onClick={() => window.close()}
            className="px-2 sm:px-3 py-1 text-xs sm:text-sm rounded hover:bg-accent text-muted-foreground hover:text-foreground shrink-0"
          >
            Close Window
          </button>
        </div>
        <div className="flex-1 overflow-auto p-2 sm:p-4">
          <WellLogPlot 
            selectedWell={selectedWell}
            projectPath={projectPath || undefined}
          />
        </div>
      </div>
    </div>
  );
}
