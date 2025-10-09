import DockPanel from "./DockPanel";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

export default function ZonationPanel({ onClose }: { onClose?: () => void }) {
  return (
    <DockPanel title="Zonation" onClose={onClose}>
      <div className="flex flex-col h-full">
        <div className="flex items-center gap-2 p-2 border-b border-card-border">
          <span className="text-sm text-foreground font-medium">Select Tags set:</span>
          <select 
            className="flex-1 h-8 px-2 text-sm bg-background border border-border rounded focus:outline-none focus:ring-2 focus:ring-ring"
            data-testid="select-tags-set"
          >
            <option value="">Select...</option>
          </select>
        </div>
        <div className="flex-1 overflow-auto p-3">
          <div className="space-y-2">
            {[1, 2, 3, 4, 5, 6, 7, 8].map((num) => (
              <div
                key={num}
                className="h-8 bg-primary/10 border-l-4 border-primary flex items-center px-2"
                data-testid={`zonation-item-${num}`}
              />
            ))}
          </div>
        </div>
        <div className="p-2 border-t border-card-border">
          <Button size="sm" variant="ghost" className="w-full" data-testid="button-view-all">
            View All
          </Button>
        </div>
      </div>
    </DockPanel>
  );
}
