import DockablePanel from "./DockablePanel";
import { Search } from "lucide-react";

export default function WellsPanelNew({
  onClose,
  onMinimize,
  isFloating,
  onDock,
  onFloat,
  savedPosition,
  savedSize,
  onGeometryChange,
}: {
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
  const items = ["View All", "0 to 100m", "Derivative Zone 1"];

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
        <div className="flex-1 p-3">
          <div className="w-full h-[400px] border-2 rounded-lg flex items-center justify-center text-muted-foreground"></div>
        </div>
      </div>
    </DockablePanel>
  );
}
