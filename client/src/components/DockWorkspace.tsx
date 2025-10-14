import { useState, useEffect } from "react";
import MenuBar from "./MenuBar";
import WellsPanelNew from "./WellsPanelNew";
import ZonationPanelNew from "./ZonationPanelNew";
import DataBrowserPanelNew from "./DataBrowserPanelNew";
import FeedbackPanelNew from "./FeedbackPanelNew";

interface PanelState {
  visible: boolean;
  floating: boolean;
  position?: { x: number; y: number };
  size?: { width: number; height: number };
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

  const floatPanel = (panelId: string) => {
    setPanels((prev) => ({
      ...prev,
      [panelId]: { ...prev[panelId], floating: true },
    }));
  };

  const saveLayout = () => {
    const layoutData = {
      panels,
      theme,
    };
    localStorage.setItem("dockLayout", JSON.stringify(layoutData));
    console.log("Layout and theme saved!");
  };

  const loadLayout = () => {
    const saved = localStorage.getItem("dockLayout");
    if (saved) {
      const layoutData = JSON.parse(saved);
      if (layoutData.panels) {
        setPanels(layoutData.panels);
      }
      if (layoutData.theme) {
        setTheme(layoutData.theme);
      }
      console.log("Layout and theme loaded!");
    }
  };

  const updatePanelGeometry = (
    panelId: string,
    position: { x: number; y: number },
    size: { width: number; height: number },
  ) => {
    setPanels((prev) => ({
      ...prev,
      [panelId]: { ...prev[panelId], position, size },
    }));
  };

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  const visiblePanels = new Set(
    Object.entries(panels)
      .filter(([_, state]) => state.visible)
      .map(([id]) => id),
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
              <WellsPanelNew
                onClose={() => closePanel("wells")}
                onFloat={() => floatPanel("wells")}
              />
            </div>
          )}
          {panels.zonation.visible && !panels.zonation.floating && (
            <div className="flex-1">
              <ZonationPanelNew
                onClose={() => closePanel("zonation")}
                onFloat={() => floatPanel("zonation")}
              />
            </div>
          )}
        </div>

        <div className="flex-1 flex flex-col gap-1">
          {panels.dataBrowser.visible && !panels.dataBrowser.floating && (
            <div className="flex-[2]">
              <DataBrowserPanelNew
                onClose={() => closePanel("dataBrowser")}
                onFloat={() => floatPanel("dataBrowser")}
              />
            </div>
          )}
          {panels.feedback.visible && !panels.feedback.floating && (
            <div className="flex-1">
              <FeedbackPanelNew
                onClose={() => closePanel("feedback")}
                onFloat={() => floatPanel("feedback")}
              />
            </div>
          )}
        </div>

        {panels.wells.visible && panels.wells.floating && (
          <WellsPanelNew
            onClose={() => closePanel("wells")}
            isFloating={true}
            onDock={() => dockPanel("wells")}
            savedPosition={panels.wells.position}
            savedSize={panels.wells.size}
            onGeometryChange={(pos, size) =>
              updatePanelGeometry("wells", pos, size)
            }
          />
        )}
        {panels.zonation.visible && panels.zonation.floating && (
          <ZonationPanelNew
            onClose={() => closePanel("zonation")}
            isFloating={true}
            onDock={() => dockPanel("zonation")}
            savedPosition={panels.zonation.position}
            savedSize={panels.zonation.size}
            onGeometryChange={(pos, size) =>
              updatePanelGeometry("zonation", pos, size)
            }
          />
        )}
        {panels.dataBrowser.visible && panels.dataBrowser.floating && (
          <DataBrowserPanelNew
            onClose={() => closePanel("dataBrowser")}
            isFloating={true}
            onDock={() => dockPanel("dataBrowser")}
            savedPosition={panels.dataBrowser.position}
            savedSize={panels.dataBrowser.size}
            onGeometryChange={(pos, size) =>
              updatePanelGeometry("dataBrowser", pos, size)
            }
          />
        )}
        {panels.feedback.visible && panels.feedback.floating && (
          <FeedbackPanelNew
            onClose={() => closePanel("feedback")}
            isFloating={true}
            onDock={() => dockPanel("feedback")}
            savedPosition={panels.feedback.position}
            savedSize={panels.feedback.size}
            onGeometryChange={(pos, size) =>
              updatePanelGeometry("feedback", pos, size)
            }
          />
        )}
      </div>
    </div>
  );
}
