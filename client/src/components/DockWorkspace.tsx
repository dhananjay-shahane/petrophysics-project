import { useState, useEffect } from "react";
import MenuBar from "./MenuBar";
import WellsPanelNew from "./WellsPanelNew";
import ZonationPanelNew from "./ZonationPanelNew";
import DataBrowserPanelNew from "./DataBrowserPanelNew";
import FeedbackPanelNew from "./FeedbackPanelNew";

interface PanelState {
  visible: boolean;
  floating: boolean;
}

export default function DockWorkspace() {
  const [panels, setPanels] = useState<Record<string, PanelState>>({
    wells: { visible: true, floating: false },
    zonation: { visible: true, floating: false },
    dataBrowser: { visible: true, floating: false },
    feedback: { visible: true, floating: false },
  });

  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [theme]);

  const togglePanel = (panelId: string) => {
    setPanels((prev) => ({
      ...prev,
      [panelId]: {
        ...prev[panelId],
        visible: !prev[panelId].visible,
      },
    }));
  };

  const closePanel = (panelId: string) => {
    setPanels((prev) => ({
      ...prev,
      [panelId]: { ...prev[panelId], visible: false },
    }));
  };

  const dockPanel = (panelId: string) => {
    setPanels((prev) => ({
      ...prev,
      [panelId]: { ...prev[panelId], floating: false },
    }));
  };

  const saveLayout = () => {
    localStorage.setItem("dockLayout", JSON.stringify(panels));
    console.log("Layout saved!");
  };

  const loadLayout = () => {
    const saved = localStorage.getItem("dockLayout");
    if (saved) {
      setPanels(JSON.parse(saved));
      console.log("Layout loaded!");
    }
  };

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  const visiblePanels = new Set(
    Object.entries(panels)
      .filter(([_, state]) => state.visible)
      .map(([id]) => id)
  );

  return (
    <div className="h-screen w-full flex flex-col bg-[#D0E8EA] dark:bg-background overflow-hidden">
      <MenuBar
        onTogglePanel={togglePanel}
        visiblePanels={visiblePanels}
        onSaveLayout={saveLayout}
        onLoadLayout={loadLayout}
        theme={theme}
        onToggleTheme={toggleTheme}
      />

      <div className="flex-1 relative flex gap-1 p-1">
        <div className="w-48 flex flex-col gap-1">
          {panels.wells.visible && !panels.wells.floating && (
            <div className="flex-1">
              <WellsPanelNew onClose={() => closePanel("wells")} />
            </div>
          )}
          {panels.zonation.visible && !panels.zonation.floating && (
            <div className="flex-1">
              <ZonationPanelNew onClose={() => closePanel("zonation")} />
            </div>
          )}
        </div>

        <div className="flex-1 flex flex-col gap-1">
          {panels.dataBrowser.visible && !panels.dataBrowser.floating && (
            <div className="flex-[2]">
              <DataBrowserPanelNew onClose={() => closePanel("dataBrowser")} />
            </div>
          )}
          {panels.feedback.visible && !panels.feedback.floating && (
            <div className="flex-1">
              <FeedbackPanelNew onClose={() => closePanel("feedback")} />
            </div>
          )}
        </div>

        {panels.wells.visible && panels.wells.floating && (
          <WellsPanelNew
            onClose={() => closePanel("wells")}
            isFloating={true}
            onDock={() => dockPanel("wells")}
          />
        )}
        {panels.zonation.visible && panels.zonation.floating && (
          <ZonationPanelNew
            onClose={() => closePanel("zonation")}
            isFloating={true}
            onDock={() => dockPanel("zonation")}
          />
        )}
        {panels.dataBrowser.visible && panels.dataBrowser.floating && (
          <DataBrowserPanelNew
            onClose={() => closePanel("dataBrowser")}
            isFloating={true}
            onDock={() => dockPanel("dataBrowser")}
          />
        )}
        {panels.feedback.visible && panels.feedback.floating && (
          <FeedbackPanelNew
            onClose={() => closePanel("feedback")}
            isFloating={true}
            onDock={() => dockPanel("feedback")}
          />
        )}
      </div>
    </div>
  );
}
