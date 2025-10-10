import DockablePanel from "./DockablePanel";
import { Search, FileText } from "lucide-react";
import { useState } from "react";
import type { WellData } from "./AdvancedDockWorkspace";

export default function WellsPanelNew({
  wells = [],
  selectedWell,
  onWellSelect,
  onClose,
  onMinimize,
  isFloating,
  onDock,
  onFloat,
  savedPosition,
  savedSize,
  onGeometryChange,
}: {
  wells?: WellData[];
  selectedWell?: WellData | null;
  onWellSelect?: (well: WellData) => void;
  onClose?: () => void;
  onMinimize?: () => void;
  isFloating?: boolean;
  onDock?: () => void;
  onFloat?: () => void;
  savedPosition?: { x: number; y: number };
  savedSize?: { width: number; height: number };
  onGeometryChange?: (
    pos: { x: number; y: number },
    size: { width: number; height: number },
  ) => void;
}) {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredWells = wells.filter(well => 
    well.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <DockablePanel
      id="wells"
      title="Wells"
      onClose={onClose}
      onMinimize={onMinimize}
      isFloating={isFloating}
      onDock={onDock}
      onFloat={onFloat}
      savedPosition={savedPosition}
      savedSize={savedSize}
      onGeometryChange={onGeometryChange}
    >
      <div className="flex flex-col h-full p-2">
        <div className="relative mb-2">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full h-8 pl-8 pr-3 text-sm bg-background border border-border rounded focus:outline-none focus:ring-2 focus:ring-ring"
            data-testid="input-search-wells"
          />
        </div>
        
        <div className="flex-1 overflow-auto">
          {wells.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
              <FileText className="w-12 h-12 mb-2 opacity-30" />
              <p className="text-sm">No wells loaded</p>
              <p className="text-xs mt-1">Load CSV/LAS files from Feedback panel</p>
            </div>
          ) : filteredWells.length === 0 ? (
            <div className="flex items-center justify-center h-full text-muted-foreground text-sm">
              No wells match your search
            </div>
          ) : (
            <div className="space-y-1">
              {filteredWells.map((well) => (
                <div
                  key={well.id}
                  onClick={() => onWellSelect?.(well)}
                  className={`flex items-center gap-2 p-2 hover:bg-accent rounded cursor-pointer transition-colors ${
                    selectedWell?.id === well.id ? 'bg-primary/20 border border-primary' : ''
                  }`}
                  title={well.path}
                >
                  <FileText className={`w-4 h-4 flex-shrink-0 ${
                    selectedWell?.id === well.id ? 'text-primary' : 'text-muted-foreground'
                  }`} />
                  <span className="text-sm truncate font-medium">{well.name}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </DockablePanel>
  );
}
