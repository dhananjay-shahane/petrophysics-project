import DockablePanel from "./DockablePanel";
import { Button } from "@/components/ui/button";

export default function ZonationPanelNew({ 
  onClose, 
  isFloating,
  onDock,
  onFloat,
  savedPosition,
  savedSize,
  onGeometryChange
}: { 
  onClose?: () => void;
  isFloating?: boolean;
  onDock?: () => void;
  onFloat?: () => void;
  savedPosition?: { x: number; y: number };
  savedSize?: { width: number; height: number };
  onGeometryChange?: (pos: { x: number; y: number }, size: { width: number; height: number }) => void;
}) {
  return (
    <DockablePanel 
      id="zonation" 
      title="Zonation" 
      onClose={onClose}
      isFloating={isFloating}
      onDock={onDock}
      onFloat={onFloat}
      savedPosition={savedPosition}
      savedSize={savedSize}
      onGeometryChange={onGeometryChange}
    >
      <div className="flex flex-col h-full">
        <div className="flex items-center gap-2 p-2 border-b border-border">
          <span className="text-sm text-foreground font-medium whitespace-nowrap">Select Tops set:</span>
          <input 
            type="text"
            className="flex-1 h-8 px-2 text-sm bg-background border border-border rounded focus:outline-none focus:ring-2 focus:ring-ring"
            data-testid="input-tops-set"
          />
          <Button size="sm" variant="outline" data-testid="button-browse">...</Button>
        </div>
        <div className="flex-1 overflow-auto p-2">
          <div className="space-y-1">
            {Array.from({ length: 8 }, (_, i) => (
              <div
                key={i}
                className="h-7 bg-[#B8D8DC]/30 dark:bg-primary/10 border-l-4 border-[#4A9FA8] dark:border-primary"
                data-testid={`zonation-bar-${i}`}
              />
            ))}
          </div>
        </div>
        <div className="p-2 border-t border-border">
          <select 
            className="w-full h-8 px-2 text-sm bg-background border border-border rounded focus:outline-none focus:ring-2 focus:ring-ring"
            data-testid="select-zone"
          >
            <option>Select zone...</option>
          </select>
        </div>
      </div>
    </DockablePanel>
  );
}
