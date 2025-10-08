import DockablePanel from "./DockablePanel";
import { Search } from "lucide-react";

export default function WellsPanelNew({ 
  onClose, 
  isFloating,
  onDock 
}: { 
  onClose?: () => void;
  isFloating?: boolean;
  onDock?: () => void;
}) {
  const items = ["View All", "0 to 100m", "Derivative Zone 1"];

  return (
    <DockablePanel 
      id="wells" 
      title="Wells" 
      onClose={onClose}
      isFloating={isFloating}
      onDock={onDock}
    >
      <div className="p-2">
        <div className="relative mb-2">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search..."
            className="w-full h-8 pl-8 pr-3 text-sm bg-background border border-border rounded focus:outline-none focus:ring-2 focus:ring-ring"
            data-testid="input-search-wells"
          />
        </div>
        <div className="space-y-1">
          {items.map((item, idx) => (
            <div
              key={idx}
              className="px-2 py-1.5 text-sm text-foreground hover-elevate cursor-pointer rounded"
              data-testid={`well-item-${idx}`}
            >
              {item}
            </div>
          ))}
        </div>
      </div>
    </DockablePanel>
  );
}
