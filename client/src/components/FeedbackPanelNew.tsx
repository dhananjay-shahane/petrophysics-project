import DockablePanel from "./DockablePanel";
import { Button } from "@/components/ui/button";

export default function FeedbackPanelNew({ 
  onClose, 
  isFloating,
  onDock 
}: { 
  onClose?: () => void;
  isFloating?: boolean;
  onDock?: () => void;
}) {
  return (
    <DockablePanel 
      id="feedback" 
      title="Feedback" 
      onClose={onClose}
      isFloating={isFloating}
      onDock={onDock}
    >
      <div className="flex flex-col h-full p-3 gap-3">
        <div className="flex gap-2">
          <Button size="sm" variant="outline" data-testid="button-load-log">Load Log</Button>
          <Button size="sm" variant="outline" data-testid="button-load-csv">Load CSV</Button>
        </div>
        <div className="flex-1">
          <textarea
            className="w-full h-full p-3 text-sm bg-background border border-border rounded resize-none focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="Drop and drag files here or use the load buttons..."
            data-testid="textarea-feedback"
          />
        </div>
      </div>
    </DockablePanel>
  );
}
