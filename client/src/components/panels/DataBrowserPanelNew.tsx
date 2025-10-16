import DockablePanel from "../workspace/DockablePanel";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { WellData } from "../workspace/Workspace";
import { ExternalLink } from "lucide-react";
import NewWindow from "react-new-window";

interface WellLog {
  name: string;
  date: string;
  description: string;
  dtst: string;
  interpolation: string;
  log_type: string;
  log: any[];
}

interface Constant {
  name: string;
  value: any;
  tag: string;
}

interface Dataset {
  name: string;
  type: string;
  wellname: string;
  well_logs: WellLog[];
  constants: Constant[];
  index_log: any[];
  index_name: string;
}

export default function DataBrowserPanelNew({
  onClose,
  onMinimize,
  isFloating,
  onDock,
  onFloat,
  savedPosition,
  savedSize,
  onGeometryChange,
  selectedWell,
  onGeneratePlot,
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
  selectedWell?: WellData | null;
  onGeneratePlot?: (logNames: string[]) => void;
}) {
  const [activeTab, setActiveTab] = useState("logs");
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [expandedTypes, setExpandedTypes] = useState<Set<string>>(
    new Set(["Special", "Point", "Continuous"]),
  );
  const [isNewWindowOpen, setIsNewWindowOpen] = useState(false);
  const [checkedLogs, setCheckedLogs] = useState<Set<string>>(new Set());
  const [checkedConstants, setCheckedConstants] = useState<Set<string>>(new Set());

  const DATASET_COLORS = {
    Special: "bg-orange-100 dark:bg-orange-900/30",
    Point: "bg-green-100 dark:bg-green-900/30",
    Continuous: "bg-blue-100 dark:bg-blue-900/30",
  };

  useEffect(() => {
    const loadWellData = async () => {
      if (!selectedWell?.path) {
        setDatasets([]);
        setSelectedDataset(null);
        return;
      }

      try {
        const response = await fetch(
          `/api/wells/data?wellPath=${encodeURIComponent(selectedWell.path)}`,
        );

        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
          const data = await response.json();
          if (response.ok && data.datasets && Array.isArray(data.datasets)) {
            setDatasets(data.datasets);
            if (data.datasets.length > 0) {
              setSelectedDataset(data.datasets[0]);
            }
          } else if (!response.ok) {
            console.error(
              "Error loading well data:",
              data.error || "Unknown error",
            );
          }
        } else {
          const text = await response.text();
          console.error(
            "Error loading well data: Server returned non-JSON response",
            text.substring(0, 100),
          );
        }
      } catch (error) {
        console.error("Error loading well data:", error);
      }
    };

    loadWellData();
  }, [selectedWell]);

  const tabs = [
    { id: "logs", label: "Logs" },
    { id: "logValues", label: "Log Values" },
    { id: "constants", label: "Constants" },
  ];

  const groupedDatasets = datasets.reduce(
    (acc, dataset) => {
      if (!acc[dataset.type]) {
        acc[dataset.type] = [];
      }
      acc[dataset.type].push(dataset);
      return acc;
    },
    {} as Record<string, Dataset[]>,
  );

  const toggleType = (type: string) => {
    const newExpanded = new Set(expandedTypes);
    if (newExpanded.has(type)) {
      newExpanded.delete(type);
    } else {
      newExpanded.add(type);
    }
    setExpandedTypes(newExpanded);
  };

  const handleDatasetClick = (dataset: Dataset) => {
    setSelectedDataset(dataset);
    setCheckedLogs(new Set());
    setCheckedConstants(new Set());
  };

  const handleLogCheckboxChange = (logName: string) => {
    setCheckedLogs((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(logName)) {
        newSet.delete(logName);
      } else {
        newSet.add(logName);
      }
      console.log('[DataBrowser] Checked logs:', Array.from(newSet));
      
      // Auto-generate plot when logs are selected
      const selectedLogNames = Array.from(newSet);
      if (selectedLogNames.length > 0 && onGeneratePlot) {
        console.log('[DataBrowser] Auto-generating plot for:', selectedLogNames);
        onGeneratePlot(selectedLogNames);
      }
      
      return newSet;
    });
  };

  const handleConstantCheckboxChange = (constantName: string) => {
    setCheckedConstants((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(constantName)) {
        newSet.delete(constantName);
      } else {
        newSet.add(constantName);
      }
      return newSet;
    });
  };

  const handleGeneratePlot = () => {
    const selectedLogNames = Array.from(checkedLogs);
    console.log('[DataBrowser] Generate plot clicked with logs:', selectedLogNames);
    if (selectedLogNames.length > 0 && onGeneratePlot) {
      onGeneratePlot(selectedLogNames);
    } else {
      console.log('[DataBrowser] Cannot generate: no logs selected or no callback');
    }
  };

  const renderLogsTab = () => {
    if (!selectedDataset?.well_logs) {
      return (
        <div className="text-center text-muted-foreground py-8">
          No logs available
        </div>
      );
    }

    return (
      <table className="w-full text-sm max-w-24">
        <thead className="sticky top-0 bg-muted dark:bg-card border-b border-border">
          <tr className="h-10">
            <th className="w-8 px-2"></th>
            <th className="px-4 py-2 text-left font-semibold text-foreground">
              Name
            </th>
            <th className="px-4 py-2 text-left font-semibold text-foreground">
              Date
            </th>
            <th className="px-4 py-2 text-left font-semibold text-foreground">
              Description
            </th>
            <th className="px-4 py-2 text-left font-semibold text-foreground">
              DTST
            </th>
            <th className="px-4 py-2 text-left font-semibold text-foreground">
              Interpolation
            </th>
            <th className="px-4 py-2 text-left font-semibold text-foreground">
              Type
            </th>
          </tr>
        </thead>
        <tbody>
          {selectedDataset.well_logs.map((log, index) => (
            <tr key={index} className="border-b border-border hover:bg-accent">
              <td className="px-2">
                <input 
                  type="checkbox" 
                  className="cursor-pointer" 
                  checked={checkedLogs.has(log.name)}
                  onChange={() => handleLogCheckboxChange(log.name)}
                />
              </td>
              <td className="px-4 py-2 text-foreground">{log.name}</td>
              <td className="px-4 py-2 text-foreground">{log.date}</td>
              <td className="px-4 py-2 text-foreground">{log.description}</td>
              <td className="px-4 py-2 text-foreground">{log.dtst}</td>
              <td className="px-4 py-2 text-foreground">{log.interpolation}</td>
              <td className="px-4 py-2 text-foreground">{log.log_type}</td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  const renderLogValuesTab = () => {
    if (!selectedDataset?.well_logs || selectedDataset.well_logs.length === 0) {
      return (
        <div className="text-center text-muted-foreground py-8">
          No log values available
        </div>
      );
    }

    const numReadings = selectedDataset.well_logs[0]?.log?.length || 0;

    return (
      <table className="w-full text-sm max-w-24">
        <thead className="sticky top-0 bg-muted dark:bg-card border-b border-border">
          <tr className="h-10">
            {selectedDataset.well_logs.map((log, index) => (
              <th
                key={index}
                className="px-4 py-2 text-left font-semibold text-foreground border-r border-border"
              >
                {log.name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: numReadings }, (_, rowIndex) => (
            <tr
              key={rowIndex}
              className="border-b border-border hover:bg-accent"
            >
              {selectedDataset.well_logs.map((log, colIndex) => (
                <td
                  key={colIndex}
                  className="px-4 py-2 text-foreground border-r border-border"
                >
                  {log.log[rowIndex] !== null && log.log[rowIndex] !== undefined
                    ? log.log[rowIndex]
                    : "-"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  const renderConstantsTab = () => {
    if (!selectedDataset?.constants || selectedDataset.constants.length === 0) {
      return (
        <div className="text-center text-muted-foreground py-8">
          No constants available
        </div>
      );
    }

    return (
      <table className="w-full text-sm">
        <thead className="sticky top-0 bg-muted dark:bg-card border-b border-border">
          <tr className="h-10">
            <th className="w-8 px-2"></th>
            <th className="px-4 py-2 text-left font-semibold text-foreground">
              Name
            </th>
            <th className="px-4 py-2 text-left font-semibold text-foreground">
              Value
            </th>
            <th className="px-4 py-2 text-left font-semibold text-foreground">
              Tag
            </th>
          </tr>
        </thead>
        <tbody>
          {selectedDataset.constants.map((constant, index) => (
            <tr key={index} className="border-b border-border hover:bg-accent">
              <td className="px-2">
                <input 
                  type="checkbox" 
                  className="cursor-pointer"
                  checked={checkedConstants.has(constant.name)}
                  onChange={() => handleConstantCheckboxChange(constant.name)}
                />
              </td>
              <td className="px-4 py-2 text-foreground">{constant.name}</td>
              <td className="px-4 py-2 text-foreground">{constant.value}</td>
              <td className="px-4 py-2 text-foreground">{constant.tag}</td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  const handleOpenInNewWindow = () => {
    setIsNewWindowOpen(true);
  };

  const handleCloseNewWindow = () => {
    setIsNewWindowOpen(false);
  };

  const dataBrowserContent = (
    <div className="flex h-full max-h-[600px] overflow-scroll">
      <div className="w-64 border-r border-border bg-muted dark:bg-card/50 flex flex-col">
        <div className="p-3 border-b border-border">
          <div className="text-sm font-medium text-foreground">
            {selectedWell?.name || "No well selected"}
          </div>
        </div>

        <div className="flex-1 overflow-auto p-2">
          {Object.entries(groupedDatasets).map(([type, typeDatasets]) => (
            <div key={type} className="mb-2">
              <button
                onClick={() => toggleType(type)}
                className={`w-full text-left px-3 py-2 rounded font-medium text-sm flex items-center justify-between text-foreground ${DATASET_COLORS[type as keyof typeof DATASET_COLORS] || "bg-accent"}`}
              >
                <span>{type}</span>
                <span>{expandedTypes.has(type) ? "▼" : "▶"}</span>
              </button>
              {expandedTypes.has(type) && (
                <div className="ml-4 mt-1 space-y-1">
                  {typeDatasets.map((dataset, index) => (
                    <button
                      key={index}
                      onClick={() => handleDatasetClick(dataset)}
                      className={`w-full text-left px-3 py-1.5 rounded text-sm transition-colors ${
                        selectedDataset === dataset
                          ? "bg-primary text-primary-foreground"
                          : "hover:bg-accent text-foreground"
                      }`}
                    >
                      {dataset.name}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
          {datasets.length === 0 && (
            <div className="text-sm text-muted-foreground p-3">
              No datasets available
            </div>
          )}
        </div>
      </div>

      <div className="flex-1 flex flex-col min-h-0">
        <div className="flex h-10 bg-secondary dark:bg-card border-b border-border shrink-0">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`px-6 py-2 text-sm font-medium border-r border-border transition-colors ${
                activeTab === tab.id
                  ? "bg-white dark:bg-background text-foreground"
                  : "text-muted-foreground hover:bg-accent"
              }`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="flex gap-2 p-2 bg-muted dark:bg-card/30 border-b border-border shrink-0">
          <Button size="sm" variant="outline">
            Delete
          </Button>
          <Button size="sm" variant="outline">
            Add
          </Button>
          <Button size="sm" variant="outline">
            Export
          </Button>
        </div>

        <div className="flex-1 overflow-auto bg-white dark:bg-background min-h-0">
          {activeTab === "logs" && renderLogsTab()}
          {activeTab === "logValues" && renderLogValuesTab()}
          {activeTab === "constants" && renderConstantsTab()}
        </div>
      </div>
    </div>
  );

  return (
    <>
      <DockablePanel
        id="dataBrowser"
        title="Data Browser"
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
        {dataBrowserContent}
      </DockablePanel>

      {isNewWindowOpen && (
        <NewWindow
          title="Data Browser"
          onUnload={handleCloseNewWindow}
          features={{
            width: 1000,
            height: 700,
            left: (window.screen.width - 1000) / 2,
            top: (window.screen.height - 700) / 2,
          }}
        >
          <div style={{ width: "100%", height: "100vh", overflow: "auto" }}>
            {dataBrowserContent}
          </div>
        </NewWindow>
      )}
    </>
  );
}
