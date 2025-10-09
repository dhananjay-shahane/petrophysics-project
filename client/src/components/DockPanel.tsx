import { X, Minus, Maximize2, GripVertical } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState, ReactNode } from "react";

interface DockPanelProps {
  title: string;
  children: ReactNode;
  onClose?: () => void;
  onMinimize?: () => void;
  onMaximize?: () => void;
  className?: string;
}

export default function DockPanel({
  title,
  children,
  onClose,
  onMinimize,
  onMaximize,
  className = "",
}: DockPanelProps) {
  const [isMaximized, setIsMaximized] = useState(false);

  const handleMaximize = () => {
    setIsMaximized(!isMaximized);
    onMaximize?.();
  };

  return (
    <div className={`flex flex-col h-full bg-card border border-card-border ${className}`}>
      <div className="flex items-center justify-between h-10 px-3 py-2 bg-card border-b border-card-border cursor-move">
        <div className="flex items-center gap-2">
          <GripVertical className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm font-semibold text-card-foreground truncate">
            {title}
          </span>
        </div>
        <div className="flex items-center gap-1">
          {onMinimize && (
            <Button
              size="icon"
              variant="ghost"
              className="h-6 w-6"
              onClick={onMinimize}
              data-testid={`button-minimize-${title.toLowerCase().replace(/\s+/g, '-')}`}
            >
              <Minus className="w-3.5 h-3.5" />
            </Button>
          )}
          {onMaximize && (
            <Button
              size="icon"
              variant="ghost"
              className="h-6 w-6"
              onClick={handleMaximize}
              data-testid={`button-maximize-${title.toLowerCase().replace(/\s+/g, '-')}`}
            >
              <Maximize2 className="w-3.5 h-3.5" />
            </Button>
          )}
          {onClose && (
            <Button
              size="icon"
              variant="ghost"
              className="h-6 w-6"
              onClick={onClose}
              data-testid={`button-close-${title.toLowerCase().replace(/\s+/g, '-')}`}
            >
              <X className="w-3.5 h-3.5" />
            </Button>
          )}
        </div>
      </div>
      <div className="flex-1 overflow-auto">{children}</div>
    </div>
  );
}
