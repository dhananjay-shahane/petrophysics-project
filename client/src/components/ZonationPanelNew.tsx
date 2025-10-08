import DockablePanel from "./DockablePanel";
import { Button } from "@/components/ui/button";
import { useRef } from "react";
import { useToast } from "@/hooks/use-toast";

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
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      toast({
        title: "Tops File Selected",
        description: `Selected: ${file.name}`,
      });
    }
  };

  return (
    <>
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
        <div className="flex flex-col h-full bg-white dark:bg-card">
          <div className="flex items-center gap-2 p-3 border-b border-border">
            <span className="text-sm text-foreground font-medium whitespace-nowrap">Select Tops set:</span>
            <input 
              type="text"
              className="flex-1 h-8 px-3 text-sm bg-background border border-input rounded focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="Choose a file..."
              readOnly
              data-testid="input-tops-set"
            />
            <Button 
              size="sm" 
              variant="outline" 
              onClick={handleBrowseClick}
              className="px-3"
              data-testid="button-browse"
            >
              ...
            </Button>
          </div>
          <div className="flex-1 p-3">
            <div className="w-full h-full border-2 border-dashed border-border rounded-lg flex items-center justify-center text-muted-foreground">
              No tops loaded
            </div>
          </div>
        </div>
      </DockablePanel>
      
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        accept=".txt,.csv,.las"
        onChange={handleFileSelect}
      />
    </>
  );
}
