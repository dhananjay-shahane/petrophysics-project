import { useState } from "react";
import { Mosaic, MosaicWindow, MosaicNode } from "react-mosaic-component";
import "react-mosaic-component/react-mosaic-component.css";
import ProjectPanel from "./ProjectPanel";
import ZonationPanel from "./ZonationPanel";
import DataBrowserPanel from "./DataBrowserPanel";
import WellsPanel from "./WellsPanel";
import FeedbackPanel from "./FeedbackPanel";

type ViewId = "project" | "zonation" | "dataBrowser" | "wells" | "feedback";

const ELEMENT_MAP: Record<ViewId, JSX.Element> = {
  project: <ProjectPanel />,
  zonation: <ZonationPanel />,
  dataBrowser: <DataBrowserPanel />,
  wells: <WellsPanel />,
  feedback: <FeedbackPanel />,
};

const TITLE_MAP: Record<ViewId, string> = {
  project: "Project",
  zonation: "Zonation",
  dataBrowser: "Data Browser",
  wells: "Wells",
  feedback: "Feedback",
};

export default function DockManager() {
  const [currentNode, setCurrentNode] = useState<MosaicNode<ViewId> | null>({
    direction: "row",
    first: {
      direction: "column",
      first: "project",
      second: {
        direction: "column",
        first: "zonation",
        second: "wells",
        splitPercentage: 50,
      },
      splitPercentage: 30,
    },
    second: {
      direction: "column",
      first: "dataBrowser",
      second: "feedback",
      splitPercentage: 70,
    },
    splitPercentage: 25,
  });

  return (
    <div className="h-screen w-full bg-background">
      <Mosaic
        renderTile={(id: ViewId, path) => (
          <MosaicWindow
            path={path}
            title={TITLE_MAP[id]}
            toolbarControls={<div></div>}
            createNode={() => "project" as ViewId}
            draggable={false}
          >
            <div className="h-full">{ELEMENT_MAP[id]}</div>
          </MosaicWindow>
        )}
        value={currentNode}
        onChange={setCurrentNode}
        className="mosaic-blueprint-theme mosaic-custom"
      />
    </div>
  );
}
