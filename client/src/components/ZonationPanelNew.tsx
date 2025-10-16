import DockablePanel from "./DockablePanel";
import { Button } from "@/components/ui/button";
import { useRef, useState } from "react";
import { useToast } from "@/hooks/use-toast";
import { ExternalLink } from "lucide-react";
import NewWindow from "react-new-window";

export default function ZonationPanelNew({
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
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();
  const [isNewWindowOpen, setIsNewWindowOpen] = useState(false);

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
  const items = ["View All", "0 to 100m", "Derivative Zone 1"];

  const handleOpenInNewWindow = () => {
    setIsNewWindowOpen(true);
  };

  const handleCloseNewWindow = () => {
    setIsNewWindowOpen(false);
  };

  const zonationContent = (
    <div className="flex flex-col h-full bg-white dark:bg-card">
      <div className="flex items-center gap-2 p-3 border-b border-border">
        <span className="text-sm text-foreground font-medium whitespace-nowrap">
          Select Tops set:
        </span>
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
        <div className="w-full h-[200px] border-2 rounded-lg flex items-center justify-center text-muted-foreground">
          No tops loaded
        </div>
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
  );

  return (
    <>
      <DockablePanel
        id="zonation"
        title="Zonation"
        onClose={onClose}
        onMinimize={onMinimize}
        isFloating={isFloating}
        onDock={onDock}
        onFloat={onFloat}
        savedPosition={savedPosition}
        savedSize={savedSize}
        onGeometryChange={onGeometryChange}
        headerActions={
          <Button
            size="icon"
            variant="ghost"
            onClick={handleOpenInNewWindow}
            className="h-6 w-6"
            title="Open in New Window"
          >
            <ExternalLink className="w-3.5 h-3.5" />
          </Button>
        }
      >
        {zonationContent}
      </DockablePanel>

      {isNewWindowOpen && (
        <NewWindow
          title="Zonation"
          onUnload={handleCloseNewWindow}
          features={{
            width: 400,
            height: 600,
            left: (window.screen.width - 400) / 2,
            top: (window.screen.height - 600) / 2
          }}
        >
          <div style={{ width: '100%', height: '100vh', overflow: 'auto' }}>
            {zonationContent}
          </div>
        </NewWindow>
      )}

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
