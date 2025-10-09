import { X, Minus, Square, Maximize2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ReactNode, useState } from "react";
import { Rnd } from "react-rnd";

interface DockablePanelProps {
  id: string;
  title: string;
  children: ReactNode;
  onClose?: () => void;
  onMinimize?: () => void;
  isFloating?: boolean;
  defaultPosition?: { x: number; y: number };
  defaultSize?: { width: number; height: number };
  onDock?: () => void;
  onFloat?: () => void;
  savedPosition?: { x: number; y: number };
  savedSize?: { width: number; height: number };
  onGeometryChange?: (
    position: { x: number; y: number },
    size: { width: number; height: number }
  ) => void;
}

export default function DockablePanel({
  id,
  title,
  children,
  onClose,
  onMinimize,
  isFloating = false,
  defaultPosition = { x: 100, y: 100 },
  defaultSize = { width: 400, height: 300 },
  onDock,
  onFloat,
  savedPosition,
  savedSize,
  onGeometryChange,
}: DockablePanelProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [isFocused, setIsFocused] = useState(false);

  if (isFloating) {
    const position = savedPosition || defaultPosition;
    const size = savedSize || defaultSize;

    return (
      <Rnd
        position={{ x: position.x, y: position.y }}
        size={{ width: size.width, height: size.height }}
        minWidth={280}
        minHeight={200}
        bounds="parent"
        dragHandleClassName="drag-handle"
        className="absolute z-50"
        onDragStop={(e, d) => {
          onGeometryChange?.(
            { x: d.x, y: d.y },
            size
          );
        }}
        onResizeStop={(e, direction, ref, delta, newPosition) => {
          onGeometryChange?.(
            newPosition,
            {
              width: parseInt(ref.style.width),
              height: parseInt(ref.style.height),
            }
          );
        }}
      >
        <div 
          className={`flex flex-col h-full bg-card border-2 shadow-xl rounded transition-all duration-200 ${
            isHovered || isFocused 
              ? 'border-primary shadow-2xl shadow-primary/30' 
              : 'border-card-border'
          }`}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          tabIndex={0}
        >
          <div className="drag-handle flex items-center justify-between h-10 px-3 py-2 bg-secondary dark:bg-card border-b border-border dark:border-card-border cursor-move">
            <span className="text-sm font-semibold text-foreground dark:text-card-foreground truncate">
              {title}
            </span>
            <div className="flex items-center gap-1">
              <Button
                size="icon"
                variant="ghost"
                className="h-6 w-6"
                onClick={onMinimize}
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
          <div className="flex-1 overflow-auto bg-white dark:bg-card">{children}</div>
        </div>
      </Rnd>
    );
  }

  return (
    <div 
      className={`flex flex-col h-full bg-card border transition-all duration-200 ${
        isHovered || isFocused 
          ? 'border-2 border-primary shadow-lg shadow-primary/20' 
          : 'border border-card-border'
      }`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onFocus={() => setIsFocused(true)}
      onBlur={() => setIsFocused(false)}
      tabIndex={0}
    >
      <div className="flex items-center justify-between h-10 px-3 py-2 bg-secondary dark:bg-card border-b border-border dark:border-card-border">
        <span className="text-sm font-semibold text-foreground dark:text-card-foreground truncate">
          {title}
        </span>
        <div className="flex items-center gap-1">
          <Button
            size="icon"
            variant="ghost"
            className="h-6 w-6"
            onClick={onMinimize}
            data-testid={`button-minimize-${id}`}
          >
            <Minus className="w-3.5 h-3.5" />
          </Button>
          {onFloat && (
            <Button
              size="icon"
              variant="ghost"
              className="h-6 w-6"
              onClick={onFloat}
              data-testid={`button-float-${id}`}
            >
              <Maximize2 className="w-3.5 h-3.5" />
            </Button>
          )}
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
      <div className="flex-1 overflow-auto bg-white dark:bg-card">{children}</div>
    </div>
  );
}
