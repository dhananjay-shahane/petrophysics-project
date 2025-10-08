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

  const tabs = [
    { id: "logs", label: "Logs" },
    { id: "values", label: "Log Values" },
    { id: "constants", label: "Constants" },
  ];

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
      defaultSize={{ width: 600, height: 400 }}
    >
      <div className="flex flex-col h-full">
        <div className="text-sm text-muted-foreground p-3 border-b border-border">
          No well selected
        </div>
        
        <div className="flex h-9 bg-[#B8D8DC] dark:bg-card border-b border-[#A0C8CC] dark:border-card-border">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`px-4 py-1.5 text-sm font-medium border-r border-[#A0C8CC] dark:border-card-border transition-colors ${
                activeTab === tab.id
                  ? "bg-white dark:bg-background text-foreground"
                  : "text-[#2C5F66] dark:text-muted-foreground hover-elevate"
              }`}
              onClick={() => setActiveTab(tab.id)}
              data-testid={`tab-${tab.id}`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="flex gap-2 p-2 border-b border-border">
          <Button size="sm" variant="outline" data-testid="button-1">Button 1</Button>
          <Button size="sm" variant="outline" data-testid="button-2">Button 2</Button>
          <Button size="sm" variant="outline" data-testid="button-3">Button 3</Button>
        </div>

        <div className="flex-1 overflow-auto">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-[#B8D8DC] dark:bg-card border-b border-[#A0C8CC] dark:border-card-border">
              <tr className="h-8">
                <th className="px-3 py-2 text-left font-semibold text-[#2C5F66] dark:text-foreground bg-[#A0C8CC] dark:bg-primary/20">S</th>
                <th className="px-3 py-2 text-left font-semibold text-[#2C5F66] dark:text-foreground">Name</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-border">
                <td className="px-3 py-2 text-foreground">1</td>
                <td className="px-3 py-2 text-foreground"></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </DockablePanel>
  );
}
