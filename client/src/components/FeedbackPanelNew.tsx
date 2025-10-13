import DockablePanel from "./DockablePanel";
import { Button } from "@/components/ui/button";
import { Terminal, Trash2 } from "lucide-react";
import { useState, useEffect, useRef } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";

interface LogEntry {
  timestamp: string;
  message: string;
  type: 'info' | 'error' | 'success' | 'warning';
}

export default function FeedbackPanelNew({ 
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
  onGeometryChange?: (pos: { x: number; y: number }, size: { width: number; height: number }) => void;
}) {
  const [logs, setLogs] = useState<LogEntry[]>([
    {
      timestamp: new Date().toLocaleTimeString(),
      message: 'Python log console initialized',
      type: 'info'
    }
  ]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const addLog = (message: string, type: LogEntry['type'] = 'info') => {
    const newLog: LogEntry = {
      timestamp: new Date().toLocaleTimeString(),
      message,
      type
    };
    setLogs(prev => [...prev, newLog]);
  };

  const clearLogs = () => {
    setLogs([{
      timestamp: new Date().toLocaleTimeString(),
      message: 'Logs cleared',
      type: 'info'
    }]);
  };

  const getLogColor = (type: LogEntry['type']) => {
    switch (type) {
      case 'error':
        return 'text-red-400';
      case 'success':
        return 'text-green-400';
      case 'warning':
        return 'text-yellow-400';
      default:
        return 'text-slate-300';
    }
  };

  // Expose addLog function globally for API calls
  useEffect(() => {
    (window as any).addPythonLog = addLog;
    return () => {
      delete (window as any).addPythonLog;
    };
  }, []);

  return (
    <DockablePanel 
      id="feedback" 
      title="Python Logs" 
      onClose={onClose}
      onMinimize={onMinimize}
      isFloating={isFloating}
      onDock={onDock}
      onFloat={onFloat}
      savedPosition={savedPosition}
      savedSize={savedSize}
      onGeometryChange={onGeometryChange}
    >
      <div className="flex flex-col h-full">
        <div className="flex items-center justify-between px-3 py-2 border-b border-border bg-muted/30">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Terminal className="w-4 h-4" />
            <span>Python Execution Console</span>
          </div>
          <Button 
            size="sm" 
            variant="ghost"
            onClick={clearLogs}
            className="h-7"
          >
            <Trash2 className="w-3.5 h-3.5 mr-1.5" />
            Clear
          </Button>
        </div>
        
        <ScrollArea className="flex-1">
          <div 
            ref={scrollRef}
            className="p-3 font-mono text-xs bg-slate-950 text-slate-300 min-h-full"
          >
            {logs.map((log, index) => (
              <div key={index} className="mb-1 flex gap-2">
                <span className="text-slate-500 flex-shrink-0">[{log.timestamp}]</span>
                <span className={getLogColor(log.type)}>{log.message}</span>
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>
    </DockablePanel>
  );
}
