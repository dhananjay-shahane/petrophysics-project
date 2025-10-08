import DockablePanel from "./DockablePanel";
import { Button } from "@/components/ui/button";
import { useState } from "react";

export default function DataBrowserPanelNew({ 
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
  const [activeTab, setActiveTab] = useState("logs");
  const [tableData, setTableData] = useState<Array<{id: number, name: string, value: string, description: string}>>([]);

  const tabs = [
    { id: "logs", label: "Logs" },
    { id: "logValues", label: "Log Values" },
    { id: "constants", label: "Constants" },
  ];

  const handleDelete = () => {
    if (tableData.length > 0) {
      setTableData(tableData.slice(0, -1));
    }
  };

  const handleAdd = () => {
    const newId = tableData.length + 1;
    setTableData([...tableData, { 
      id: newId, 
      name: `Item ${newId}`, 
      value: '', 
      description: '' 
    }]);
  };

  const handleExport = () => {
    const dataStr = JSON.stringify(tableData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${activeTab}_data.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <DockablePanel 
      id="dataBrowser" 
      title="Data Browser" 
      onClose={onClose}
      isFloating={isFloating}
      onDock={onDock}
      onFloat={onFloat}
      savedPosition={savedPosition}
      savedSize={savedSize}
      onGeometryChange={onGeometryChange}
      defaultSize={{ width: 720, height: 500 }}
    >
      <div className="flex h-full">
        <div className="w-60 border-r border-[#A0C8CC] bg-[#E8F4F5] dark:bg-card/50 p-3">
          <div className="text-sm text-[#2C5F66] dark:text-muted-foreground">
            No well selected
          </div>
        </div>
        
        <div className="flex-1 flex flex-col min-h-0">
          <div className="flex h-10 bg-[#B8D8DC] dark:bg-card border-b border-[#A0C8CC] dark:border-card-border shrink-0">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                className={`px-6 py-2 text-sm font-medium border-r border-[#A0C8CC] dark:border-card-border transition-colors ${
                  activeTab === tab.id
                    ? "bg-white dark:bg-background text-[#2C5F66] dark:text-foreground"
                    : "text-[#2C5F66] dark:text-muted-foreground hover:bg-[#A0C8CC]/30"
                }`}
                onClick={() => setActiveTab(tab.id)}
                data-testid={`tab-${tab.id}`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="flex gap-2 p-2 bg-[#E8F4F5] dark:bg-card/30 border-b border-[#A0C8CC] dark:border-border shrink-0">
            <Button 
              size="sm" 
              className="bg-[#B8D8DC] hover:bg-[#A0C8CC] text-[#2C5F66] dark:text-foreground border-[#A0C8CC]" 
              variant="outline"
              onClick={handleDelete}
              data-testid="button-delete"
            >
              Delete
            </Button>
            <Button 
              size="sm" 
              className="bg-[#B8D8DC] hover:bg-[#A0C8CC] text-[#2C5F66] dark:text-foreground border-[#A0C8CC]" 
              variant="outline"
              onClick={handleAdd}
              data-testid="button-add"
            >
              Add
            </Button>
            <Button 
              size="sm" 
              className="bg-[#B8D8DC] hover:bg-[#A0C8CC] text-[#2C5F66] dark:text-foreground border-[#A0C8CC]" 
              variant="outline"
              onClick={handleExport}
              data-testid="button-export"
            >
              Export
            </Button>
          </div>

          <div className="flex-1 overflow-auto bg-white dark:bg-background min-h-0">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-[#E8F4F5] dark:bg-card border-b border-[#A0C8CC] dark:border-card-border">
                <tr className="h-10">
                  <th className="px-4 py-2 text-left font-semibold text-[#2C5F66] dark:text-foreground border-r border-[#A0C8CC] dark:border-card-border">Name</th>
                  <th className="px-4 py-2 text-left font-semibold text-[#2C5F66] dark:text-foreground border-r border-[#A0C8CC] dark:border-card-border">Value</th>
                  <th className="px-4 py-2 text-left font-semibold text-[#2C5F66] dark:text-foreground">Description</th>
                </tr>
              </thead>
              <tbody>
                {tableData.length === 0 ? (
                  <tr>
                    <td colSpan={3} className="px-4 py-8 text-center text-muted-foreground">
                      No data available. Click "Add" to create entries.
                    </td>
                  </tr>
                ) : (
                  tableData.map((row) => (
                    <tr key={row.id} className="border-b border-[#E8F4F5] dark:border-border hover:bg-[#F5FAFA] dark:hover:bg-card/30">
                      <td className="px-4 py-2 text-[#2C5F66] dark:text-foreground">{row.name}</td>
                      <td className="px-4 py-2 text-[#2C5F66] dark:text-foreground">{row.value}</td>
                      <td className="px-4 py-2 text-[#2C5F66] dark:text-foreground">{row.description}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </DockablePanel>
  );
}
