import DockablePanel from "./DockablePanel";
import { Button } from "@/components/ui/button";
import { Terminal, Trash2, Upload, FolderOpen, ExternalLink } from "lucide-react";
import { useState, useEffect, useRef } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useToast } from "@/hooks/use-toast";
import NewWindow from "react-new-window";

interface LogEntry {
  timestamp: string;
  message: string;
  type: "info" | "error" | "success" | "warning";
  icon?: string;
}

interface WellData {
  id: string;
  name: string;
  uwi?: string;
  field?: string;
  operator?: string;
  location?: string;
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
  projectPath,
  selectedWell,
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
  projectPath?: string;
  selectedWell?: WellData | null;
}) {
  const [logs, setLogs] = useState<LogEntry[]>(() => {
    const savedLogs = localStorage.getItem("feedbackLogs");
    if (savedLogs) {
      try {
        return JSON.parse(savedLogs);
      } catch {
        return [
          {
            timestamp: new Date().toLocaleTimeString(),
            message: "Feedback console initialized",
            type: "info",
            icon: "🔧",
          },
        ];
      }
    }
    return [
      {
        timestamp: new Date().toLocaleTimeString(),
        message: "Feedback console initialized",
        type: "info",
        icon: "🔧",
      },
    ];
  });
  const [lasFile, setLasFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const { toast } = useToast();
  const scrollRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const scrollEndRef = useRef<HTMLDivElement>(null);
  const [isNewWindowOpen, setIsNewWindowOpen] = useState(false);

  useEffect(() => {
    localStorage.setItem("feedbackLogs", JSON.stringify(logs));
  }, [logs]);
  // scrollEndRef.current?.scrollIntoView({ behavior: "smooth" });
  
  const addLog = (
    message: string,
    type: LogEntry["type"] = "info",
    icon?: string,
  ) => {
    const newLog: LogEntry = {
      timestamp: new Date().toLocaleTimeString(),
      message,
      type,
      icon,
    };
    setLogs((prev) => [...prev, newLog]);
  };

  const clearLogs = () => {
    const newLogs: LogEntry[] = [
      {
        timestamp: new Date().toLocaleTimeString(),
        message: "Logs cleared",
        type: "info",
        icon: "🗑️",
      },
    ];
    setLogs(newLogs);
    localStorage.setItem("feedbackLogs", JSON.stringify(newLogs));
  };

  const getLogColor = (type: LogEntry["type"]) => {
    switch (type) {
      case "error":
        return "text-red-400";
      case "success":
        return "text-green-400";
      case "warning":
        return "text-yellow-400";
      default:
        return "text-slate-300";
    }
  };

  const getIconForMessage = (
    message: string,
    type: LogEntry["type"],
  ): string => {
    if (message.includes("project") && message.toLowerCase().includes("open"))
      return "📁";
    if (message.includes("LAS") && message.includes("upload")) return "📤";
    if (message.includes("well") && message.includes("creat")) return "🔧";
    if (message.includes("[LOG PLOT]")) return "📊";
    if (message.includes("[CROSS PLOT]")) return "📈";
    if (message.includes("data") && message.includes("load")) return "🗂️";
    if (type === "error") return "⚠️";
    if (type === "success") return "✅";
    if (type === "warning") return "⚠️";
    return "📝";
  };

  useEffect(() => {
    const originalLog = console.log;
    const originalError = console.error;
    const originalWarn = console.warn;
    const originalFetch = window.fetch;

    console.log = (...args) => {
      originalLog(...args);
      const message = args
        .map((a) =>
          typeof a === "object" ? JSON.stringify(a, null, 2) : String(a),
        )
        .join(" ");

      if (
        message.includes("[LOG PLOT]") ||
        message.includes("[CROSS PLOT]") ||
        message.includes("[LogPlot]") ||
        message.includes("[CrossPlot]") ||
        message.includes("project") ||
        message.includes("well") ||
        message.includes("data") ||
        message.includes("upload")
      ) {
        const icon = getIconForMessage(message, "info");
        addLog(message, "info", icon);
      }
    };

    console.error = (...args) => {
      originalError(...args);
      const message = args
        .map((a) =>
          typeof a === "object" ? JSON.stringify(a, null, 2) : String(a),
        )
        .join(" ");
      addLog(message, "error", "⚠️");
    };

    console.warn = (...args) => {
      originalWarn(...args);
      const message = args
        .map((a) =>
          typeof a === "object" ? JSON.stringify(a, null, 2) : String(a),
        )
        .join(" ");
      addLog(message, "warning", "⚠️");
    };

    window.fetch = async (...args) => {
      const startTime = Date.now();
      const url =
        typeof args[0] === "string"
          ? args[0]
          : args[0] instanceof Request
            ? args[0].url
            : args[0]?.toString() || "unknown";
      const method = (args[1]?.method || "GET").toUpperCase();

      try {
        const response = await originalFetch(...args);
        const duration = Date.now() - startTime;

        const urlPath = url.split("?")[0];
        const wellInfo = selectedWell ? ` [Well: ${selectedWell.name}]` : "";
        let logMessage = `${method} ${urlPath} - ${response.status} (${duration}ms)${wellInfo}`;
        let logType: LogEntry["type"] = "info";
        let icon = "🌐";

        if (urlPath.includes("/api/wells/create-from-las")) {
          logMessage = `📤 LAS Upload Request - ${response.status} (${duration}ms)`;
          logType = response.ok ? "success" : "error";
          icon = "📤";
        } else if (urlPath.includes("/log-plot")) {
          logMessage = `📊 Log Plot Generation${wellInfo} - ${response.status} (${duration}ms)`;
          logType = response.ok ? "success" : "error";
          icon = "📊";
        } else if (urlPath.includes("/cross-plot")) {
          logMessage = `📈 Cross Plot Generation${wellInfo} - ${response.status} (${duration}ms)`;
          logType = response.ok ? "success" : "error";
          icon = "📈";
        } else if (urlPath.includes("/datasets")) {
          logMessage = `🗂️ Data Loading${wellInfo} - ${response.status} (${duration}ms)`;
          logType = response.ok ? "success" : "error";
          icon = "🗂️";
        } else if (urlPath.includes("/api/wells")) {
          logMessage = `🔧 Well Operation - ${response.status} (${duration}ms)`;
          logType = response.ok ? "success" : "error";
          icon = "🔧";
        }

        if (!response.ok) {
          logType = "error";
        }

        addLog(logMessage, logType, icon);

        return response;
      } catch (error) {
        const duration = Date.now() - startTime;
        const wellInfo = selectedWell ? ` [Well: ${selectedWell.name}]` : "";
        addLog(
          `❌ ${method} ${url}${wellInfo} - Failed (${duration}ms): ${error}`,
          "error",
          "⚠️",
        );
        throw error;
      }
    };

    (window as any).addAppLog = (
      message: string,
      type: LogEntry["type"] = "info",
      icon?: string,
    ) => {
      const logIcon = icon || getIconForMessage(message, type);
      addLog(message, type, logIcon);
    };

    (window as any).addPythonLog = (
      message: string,
      type: LogEntry["type"] = "info",
    ) => {
      const icon = getIconForMessage(message, type);
      addLog(message, type, icon);
    };

    return () => {
      console.log = originalLog;
      console.error = originalError;
      console.warn = originalWarn;
      window.fetch = originalFetch;
      delete (window as any).addAppLog;
      delete (window as any).addPythonLog;
    };
  }, [selectedWell]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.endsWith(".las") && !file.name.endsWith(".LAS")) {
        toast({
          title: "Error",
          description: "Please select a LAS file",
          variant: "destructive",
        });
        return;
      }
      setLasFile(file);
      addLog(`File selected: ${file.name}`, "info", "📂");
    }
  };

  const handleUpload = async () => {
    if (!lasFile) {
      toast({
        title: "Error",
        description: "Please select a LAS file",
        variant: "destructive",
      });
      return;
    }

    if (!projectPath || projectPath === "No path selected") {
      toast({
        title: "Error",
        description:
          "No project is currently open. Please open or create a project first.",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);
    addLog("📤 Starting LAS file upload...", "info", "📤");

    try {
      const formData = new FormData();
      formData.append("lasFile", lasFile);
      formData.append("projectPath", projectPath);

      const response = await fetch("/api/wells/create-from-las", {
        method: "POST",
        body: formData,
      });

      const contentType = response.headers.get("content-type");
      let result: any = {};
      
      if (contentType && contentType.includes("application/json")) {
        result = await response.json();
        
        if (result.logs && Array.isArray(result.logs)) {
          result.logs.forEach((log: any) => {
            const icon = getIconForMessage(log.message, log.type);
            addLog(log.message, log.type, icon);
          });
        }
      } else {
        const text = await response.text();
        addLog(`Server error: ${text.substring(0, 200)}`, "error", "⚠️");
        throw new Error("Server returned an error. Check feedback logs for details.");
      }

      if (!response.ok) {
        throw new Error(result.error || "Failed to create well from LAS file");
      }

      addLog(
        `✅ Well "${result.well.name}" created successfully`,
        "success",
        "✅",
      );

      toast({
        title: "Success",
        description: `Well "${result.well.name}" created successfully`,
      });

      setLasFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error: any) {
      const errorMessage =
        error.message ||
        "Failed to create well from LAS file. Please try again.";
      addLog(`❌ Upload failed: ${errorMessage}`, "error", "⚠️");

      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleOpenInNewWindow = () => {
    setIsNewWindowOpen(true);
  };

  const handleCloseNewWindow = () => {
    setIsNewWindowOpen(false);
  };

  const feedbackContent = (
    <div className="flex flex-col h-full">
      <div className="px-3 py-2 border-b border-border bg-muted/30">
        <div className="flex items-center gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept=".las,.LAS"
            onChange={handleFileChange}
            className="hidden"
            id="las-upload"
          />
          <label htmlFor="las-upload" className="cursor-pointer">
            <Button
              size="sm"
              variant="outline"
              className="h-8"
              asChild
              disabled={isUploading}
            >
              <span>
                <FolderOpen className="w-3.5 h-3.5 mr-1.5" />
                Choose LAS File
              </span>
            </Button>
          </label>

          {lasFile && (
            <span className="text-xs text-muted-foreground truncate flex-1">
              {lasFile.name}
            </span>
          )}

          <Button
            size="sm"
            onClick={handleUpload}
            disabled={!lasFile || isUploading}
            className="h-8"
          >
            <Upload className="w-3.5 h-3.5 mr-1.5" />
            {isUploading ? "Uploading..." : "Upload"}
          </Button>
        </div>
      </div>

      <div className="flex items-center justify-between px-3 py-2 border-b border-border bg-muted/30">
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4" />
            <span>System Logs</span>
          </div>
          {selectedWell && (
            <div className="flex items-center gap-2 text-xs bg-slate-800 px-2 py-1 rounded">
              <span className="text-blue-400">🔹</span>
              <span className="text-slate-300">{selectedWell.name}</span>
            </div>
          )}
        </div>
        <Button size="sm" variant="ghost" onClick={clearLogs} className="h-7">
          <Trash2 className="w-3.5 h-3.5 mr-1.5" />
          Clear
        </Button>
      </div>

      <div className="flex-1 overflow-hidden max-h-[400px]">
        <div
          ref={scrollRef}
          className="h-full max-h-[400px] overflow-y-auto p-3 font-mono text-xs bg-slate-950 text-slate-300"
        >
          {logs.map((log, index) => (
            <div key={index} className="mb-1 flex gap-2">
              <span className="text-slate-500 flex-shrink-0">
                [{log.timestamp}]
              </span>
              {log.icon && <span className="flex-shrink-0">{log.icon}</span>}
              <span className={getLogColor(log.type)}>{log.message}</span>
            </div>
          ))}
          <div ref={scrollEndRef} />
        </div>
      </div>
    </div>
  );

  return (
    <>
      <DockablePanel
        id="feedback"
        title="Feedback Logs"
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
        {feedbackContent}
      </DockablePanel>

      {isNewWindowOpen && (
        <NewWindow
          title="Feedback Logs"
          onUnload={handleCloseNewWindow}
          features={{
            width: 800,
            height: 600,
            left: (window.screen.width - 800) / 2,
            top: (window.screen.height - 600) / 2
          }}
        >
          <div style={{ width: '100%', height: '100vh', overflow: 'auto' }}>
            {feedbackContent}
          </div>
        </NewWindow>
      )}
    </>
  );
}
