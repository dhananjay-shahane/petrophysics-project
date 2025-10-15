import DockablePanel from "./DockablePanel";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { WellData } from "./AdvancedDockWorkspace";

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
}) {
  const [activeTab, setActiveTab] = useState("logs");
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [expandedTypes, setExpandedTypes] = useState<Set<string>>(
    new Set(["Special", "Point", "Continuous"]),
  );

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
        if (response.ok) {
          const data = await response.json();
          if (data.datasets && Array.isArray(data.datasets)) {
            setDatasets(data.datasets);
            if (data.datasets.length > 0) {
              setSelectedDataset(data.datasets[0]);
            }
          }
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
            <th className="px-4 py-2 text-left font-semibold">Name</th>
            <th className="px-4 py-2 text-left font-semibold">Date</th>
            <th className="px-4 py-2 text-left font-semibold">Description</th>
            <th className="px-4 py-2 text-left font-semibold">DTST</th>
            <th className="px-4 py-2 text-left font-semibold">Interpolation</th>
            <th className="px-4 py-2 text-left font-semibold">Type</th>
          </tr>
        </thead>
        <tbody>
          {selectedDataset.well_logs.map((log, index) => (
            <tr key={index} className="border-b border-border hover:bg-accent">
              <td className="px-2">
                <input type="checkbox" className="cursor-pointer" />
              </td>
              <td className="px-4 py-2">{log.name}</td>
              <td className="px-4 py-2">{log.date}</td>
              <td className="px-4 py-2">{log.description}</td>
              <td className="px-4 py-2">{log.dtst}</td>
              <td className="px-4 py-2">{log.interpolation}</td>
              <td className="px-4 py-2">{log.log_type}</td>
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
                className="px-4 py-2 text-left font-semibold border-r border-border"
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
                <td key={colIndex} className="px-4 py-2 border-r border-border">
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
            <th className="px-4 py-2 text-left font-semibold">Name</th>
            <th className="px-4 py-2 text-left font-semibold">Value</th>
            <th className="px-4 py-2 text-left font-semibold">Tag</th>
          </tr>
        </thead>
        <tbody>
          {selectedDataset.constants.map((constant, index) => (
            <tr key={index} className="border-b border-border hover:bg-accent">
              <td className="px-2">
                <input type="checkbox" className="cursor-pointer" />
              </td>
              <td className="px-4 py-2">{constant.name}</td>
              <td className="px-4 py-2">{constant.value}</td>
              <td className="px-4 py-2">{constant.tag}</td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  return (
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
    >
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
                  className={`w-full text-left px-3 py-2 rounded font-medium text-sm flex items-center justify-between ${DATASET_COLORS[type as keyof typeof DATASET_COLORS] || "bg-gray-100"}`}
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
                            : "hover:bg-accent"
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
    </DockablePanel>
  );
}
