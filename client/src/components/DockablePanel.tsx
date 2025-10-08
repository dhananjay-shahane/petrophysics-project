import { X, Minus, Square } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ReactNode, useState } from "react";
import { Rnd } from "react-rnd";

interface DockablePanelProps {
  id: string;
  title: string;
  children: ReactNode;
  onClose?: () => void;
  isFloating?: boolean;
  defaultPosition?: { x: number; y: number };
  defaultSize?: { width: number; height: number };
  onDock?: () => void;
}

export default function DockablePanel({
  id,
  title,
  children,
  onClose,
  isFloating = false,
  defaultPosition = { x: 100, y: 100 },
  defaultSize = { width: 400, height: 300 },
  onDock,
}: DockablePanelProps) {
  const [isMinimized, setIsMinimized] = useState(false);

  if (isFloating) {
    return (
      <Rnd
        default={{
          x: defaultPosition.x,
          y: defaultPosition.y,
          width: defaultSize.width,
          height: defaultSize.height,
        }}
        minWidth={280}
        minHeight={200}
        bounds="parent"
        dragHandleClassName="drag-handle"
        className="absolute z-50"
      >
        <div className="flex flex-col h-full bg-card border-2 border-card-border shadow-xl rounded">
          <div className="drag-handle flex items-center justify-between h-10 px-3 py-2 bg-[#B8D8DC] dark:bg-card border-b border-[#A0C8CC] dark:border-card-border cursor-move">
            <span className="text-sm font-semibold text-[#2C5F66] dark:text-card-foreground truncate">
              {title}
            </span>
            <div className="flex items-center gap-1">
              <Button
                size="icon"
                variant="ghost"
                className="h-6 w-6"
                onClick={() => setIsMinimized(!isMinimized)}
                data-testid={`button-minimize-${id}`}
              >
                <Minus className="w-3.5 h-3.5" />
              </Button>
              <Button
                size="icon"
                variant="ghost"
                className="h-6 w-6"
                onClick={onDock}
                data-testid={`button-dock-${id}`}
              >
                <Square className="w-3.5 h-3.5" />
              </Button>
              <Button
                size="icon"
                variant="ghost"
                className="h-6 w-6"
                onClick={onClose}
                data-testid={`button-close-${id}`}
              >
                <X className="w-3.5 h-3.5" />
              </Button>
            </div>
          </div>
          {!isMinimized && (
            <div className="flex-1 overflow-auto bg-white dark:bg-card">{children}</div>
          )}
        </div>
      </Rnd>
    );
  }

  return (
    <div className="flex flex-col h-full bg-card border border-card-border">
      <div className="flex items-center justify-between h-10 px-3 py-2 bg-[#B8D8DC] dark:bg-card border-b border-[#A0C8CC] dark:border-card-border">
        <span className="text-sm font-semibold text-[#2C5F66] dark:text-card-foreground truncate">
          {title}
        </span>
        <div className="flex items-center gap-1">
          <Button
            size="icon"
            variant="ghost"
            className="h-6 w-6"
            onClick={() => setIsMinimized(!isMinimized)}
            data-testid={`button-minimize-${id}`}
          >
            <Minus className="w-3.5 h-3.5" />
          </Button>
          <Button
            size="icon"
            variant="ghost"
            className="h-6 w-6"
            onClick={onClose}
            data-testid={`button-close-${id}`}
          >
            <X className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>
      {!isMinimized && (
        <div className="flex-1 overflow-auto bg-white dark:bg-card">{children}</div>
      )}
    </div>
  );
}
